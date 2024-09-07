import sqlite3
import datetime


class DataBase:
    def __init__(self, db_file):
        # Подключение к базе данных SQLite
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

        # Создание таблицы users, если она не существует
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT UNIQUE,  
                user_name TEXT UNIQUE,  
                volume REAL DEFAULT 0,
                attempts INTEGER DEFAULT 3,
                last_attempt_time TEXT
            );
            """
        )

        # Создание таблицы groups, если она не существует
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS groups (
                group_id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_name TEXT
            );
            """
        )

        # Создание связующей таблицы user_groups для связи пользователей с группами
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_groups (
                user_id TEXT,
                group_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (group_id) REFERENCES groups (group_id),
                PRIMARY KEY (user_id, group_id)
            );
            """
        )

        self.connection.commit()

    # Функция добавления пользователя
    def add_user(self, user_id: int, user_name: str) -> None:
        try:
            self.cursor.execute(
                'INSERT INTO users (user_id, user_name, volume, attempts, last_attempt_time) VALUES (?, ?, ?, ?, ?)',
                (user_id, user_name, 0, 3, None)
            )
            self.connection.commit()
        except sqlite3.IntegrityError:
            pass

    # Функция добавления группы
    def add_group(self, group_id: int, group_name: str) -> None:
        try:
            self.cursor.execute(
                'INSERT INTO groups (group_id, group_name) VALUES (?, ?)',
                (group_id, group_name)
            )
            self.connection.commit()
        except sqlite3.IntegrityError:
            pass

    # Функция добавления пользователя в группу
    def add_user_to_group(self, user_id: int, group_id: int) -> None:
        try:
            self.cursor.execute(
                'INSERT INTO user_groups (user_id, group_id) VALUES (?, ?)',
                (user_id, group_id)
            )
            self.connection.commit()
        except sqlite3.IntegrityError:
            pass

    # Проверка наличия пользователя
    def user_exists(self, user_id: int) -> bool:
        result = self.cursor.execute(
            "SELECT user_id FROM users WHERE user_id = ?", (user_id,)
        )
        return result.fetchone() is not None

    # Получение информации о пользователе
    def get_user(self, user_id: int = None, user_name: str = None):
        if user_id is not None:
            result = self.cursor.execute(
                'SELECT user_id, user_name FROM users WHERE user_id = ?', (user_id,)
            )
        elif user_name is not None:
            result = self.cursor.execute(
                'SELECT user_id, user_name FROM users WHERE user_name = ?', (user_name,)
            )
        else:
            raise ValueError("Необходимо указать user_id или user_name.")

        row = result.fetchone()
        return row if row else None

    # Получение всех групп пользователя
    def get_user_groups(self, user_id: int):
        self.cursor.execute(
            'SELECT g.group_id, g.group_name FROM groups g JOIN user_groups ug ON g.group_id = ug.group_id WHERE ug.user_id = ?',
            (user_id,)
        )
        result = self.cursor.fetchall()
        return result if result else None

    # Получение всех пользователей группы
    def get_group_users(self, group_id: int):
        self.cursor.execute(
            """
            SELECT users.user_id, users.user_name, users.volume 
            FROM users 
            JOIN user_groups ON users.user_id = user_groups.user_id 
            WHERE user_groups.group_id = ?
            ORDER BY users.volume DESC 
            LIMIT 10;
            """, (group_id,)
        )
        result = self.cursor.fetchall()
        return result if result else []

    def get_global_top_users(self):
        self.cursor.execute(
            """
            SELECT user_id, user_name, volume 
            FROM users 
            ORDER BY volume DESC 
            LIMIT 10;
            """
        )
        result = self.cursor.fetchall()
        return result if result else []

    def get_top_groups(self):
        self.cursor.execute(
            """
            SELECT groups.group_id, groups.group_name, SUM(users.volume) AS total_volume
            FROM users
            JOIN user_groups ON users.user_id = user_groups.user_id
            JOIN groups ON user_groups.group_id = groups.group_id
            GROUP BY groups.group_id, groups.group_name
            ORDER BY total_volume DESC
            LIMIT 10;
            """
        )
        result = self.cursor.fetchall()
        return result if result else []

    # Функция добавления объема к пользователю
    def add_volume(self, user_id, volume):
        self.check_attempt_reset(user_id)
        self.cursor.execute(
            'SELECT attempts FROM users WHERE user_id = ?', (user_id,)
        )
        attempts = self.cursor.fetchone()

        if attempts and attempts[0] > 0:
            self.cursor.execute(
                'UPDATE users SET volume = volume + ?, attempts = attempts - 1, last_attempt_time = ? WHERE user_id = ?',
                (round(volume, 1), datetime.datetime.now().isoformat(), user_id)
            )
            self.connection.commit()
            return True
        else:
            return False

    # Функция добавления попыток пользователю
    def add_attempts(self, user_id, attempts: int = 1):
        self.cursor.execute(
            'UPDATE users SET attempts = attempts + ?, last_attempt_time = NULL WHERE user_id = ?',
            (attempts, user_id)
        )
        self.connection.commit()

    # Получение объема для пользователя
    def get_volume(self, user_id):
        self.cursor.execute(
            'SELECT volume FROM users WHERE user_id = ?', (user_id,)
        )
        result = self.cursor.fetchone()
        return result[0] if result else None

    # Получение времени до следующей попытки
    def get_time_until_next_attempt(self, user_id):
        self.cursor.execute(
            'SELECT attempts, last_attempt_time FROM users WHERE user_id = ?', (user_id,)
        )
        result = self.cursor.fetchone()

        if result:
            attempts, last_attempt_time = result
            if attempts == 0 and last_attempt_time is not None:
                last_time = datetime.datetime.fromisoformat(last_attempt_time)
                time_elapsed = (datetime.datetime.now() - last_time).total_seconds()
                time_left = max(1800 - time_elapsed, 0)

                if time_left == 0:
                    self.cursor.execute(
                        'UPDATE users SET attempts = 1, last_attempt_time = NULL WHERE user_id = ?',
                        (user_id,)
                    )
                    self.connection.commit()
                    return "Попытки уже доступны."

                minutes, seconds = divmod(int(time_left), 60)
                if minutes == 0:
                    return f"{seconds} секунд"
                else:
                    return f"{minutes} минут {seconds} секунд"
            else:
                return "Попытки уже доступны."
        else:
            return "Пользователь не найден."

    # Проверка на восстановление попыток
    def check_attempt_reset(self, user_id):
        self.cursor.execute(
            'SELECT attempts, last_attempt_time FROM users WHERE user_id = ?', (user_id,)
        )
        result = self.cursor.fetchone()

        if result:
            attempts, last_attempt_time = result
            if attempts == 0 and last_attempt_time is None:
                self.cursor.execute(
                    'UPDATE users SET last_attempt_time = ? WHERE user_id = ?',
                    (datetime.datetime.now().isoformat(), user_id)
                )
                self.connection.commit()
                return False

            if last_attempt_time is not None:
                last_time = datetime.datetime.fromisoformat(last_attempt_time)
                if (datetime.datetime.now() - last_time).total_seconds() >= 3600:
                    self.cursor.execute(
                        'UPDATE users SET attempts = 1, last_attempt_time = NULL WHERE user_id = ?',
                        (user_id,)
                    )
                    self.connection.commit()
                    return True
        return False

    # Получение всех пользователей
    def get_all_users(self):
        self.cursor.execute(
            'SELECT * FROM users'
        )
        result = self.cursor.fetchall()
        return result if result else None
