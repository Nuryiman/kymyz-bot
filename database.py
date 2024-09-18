import sqlite3
import datetime
import threading


class DataBase:
    def __init__(self, db_file):
        # Подключение к базе данных SQLite
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

        # Создание таблицы users, если она не существует
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER UNIQUE,  
                user_name TEXT UNIQUE DEFAULT Null,
                first_name TEXT,  
                volume REAL DEFAULT 0,
                day_volume REAL DEFAULT 0,
                attempts INTEGER DEFAULT 3,
                last_attempt_time TEXT,
                bot_stop_protection BOOLEAN DEFAULT 1
            );
            """
        )

        # Создание таблицы groups, если она не существует
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS groups (
                group_id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_username,
                group_name TEXT
            );
            """
        )

        # Создание связующей таблицы user_groups для связи пользователей с группами
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_groups (
                user_id INTEGER,
                group_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (group_id) REFERENCES groups (group_id),
                PRIMARY KEY (user_id, group_id)
            );
            """
        )

        self.connection.commit()

        # Создание таблицы для рекламы
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS admin_reklams (
                title TEXT,
                href TEXT,
                inline_title TEXT
            );
            """
        )

        # Создания промежуточной таблицы для бот стоп
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users_bot_stop (
            prohibiting_user_id INTEGER,
            prohibited_user_id INTEGER,
            PRIMARY KEY (prohibiting_user_id, prohibited_user_id),
            FOREIGN KEY (prohibiting_user_id) REFERENCES users (user_id) ON DELETE CASCADE,
            FOREIGN KEY (prohibited_user_id) REFERENCES users (user_id) ON DELETE CASCADE
            );
            """
        )

        self.connection.commit()
        self.start_reset_timer()

    # Функция добавления пользователя
    def add_user(self, user_id: int, first_name: str,  user_name: str = None) -> None:
        try:
            self.cursor.execute(
                'INSERT INTO users (user_id, user_name, first_name, volume, day_volume, attempts, last_attempt_time, bot_stop_protection) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (user_id, user_name, first_name, 0, 0, 3, None, 0)
            )
            self.connection.commit()
        except sqlite3.IntegrityError:
            pass

    # Функция добавления группы
    def add_group(self, group_id: int, group_name: str, group_username: str = None) -> None:
        try:
            self.cursor.execute(
                'INSERT INTO groups (group_id, group_username, group_name) VALUES (?, ?, ?)',
                (group_id, group_username, group_name)
            )
            self.connection.commit()
        except sqlite3.IntegrityError:
            pass

    def get_all_groups(self):
        self.cursor.execute(
            'SELECT group_id FROM groups'
        )
        result = self.cursor.fetchall()
        return [row[0] for row in result] if result else []

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
            SELECT users.user_id, users.first_name, users.volume 
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
            SELECT user_id, first_name, volume 
            FROM users 
            ORDER BY volume DESC 
            LIMIT 10;
            """
        )
        result = self.cursor.fetchall()
        return result if result else []

    def get_global_day_top_users(self):
        self.cursor.execute(
            """
            SELECT user_id, first_name, day_volume 
            FROM users 
            ORDER BY day_volume DESC 
            LIMIT 10;
            """
        )
        result = self.cursor.fetchall()

        return result if result else []

    def get_top_groups(self):
        self.cursor.execute(
            """
            SELECT groups.group_id, groups.group_username, groups.group_name, SUM(users.volume) AS total_volume
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

    def get_day_top_groups(self):
        self.cursor.execute(
            """
            SELECT groups.group_id, groups.group_username, groups.group_name, SUM(users.day_volume) AS total_volume
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
                'UPDATE users SET volume = volume + ?, day_volume = day_volume + ?,'
                ' attempts = attempts - 1, last_attempt_time = ? WHERE user_id = ?',
                (round(volume, 1), round(volume, 1), datetime.datetime.now().isoformat(), user_id)
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
                time_left = max(3600 - time_elapsed, 0)

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

    # Функция обнуления day_volume
    def start_reset_timer(self):
        self.reset_day_volume()  # Сброс значения сразу при запуске
        self.schedule_next_reset()

    def schedule_next_reset(self):
        # Запускаем таймер, чтобы вызвать функцию через 24 часа (86400 секунд)
        threading.Timer(86400, self.reset_day_volume).start()

    def reset_day_volume(self):
        """Сбрасывает колонку day_volume для всех пользователей."""
        self.cursor.execute('UPDATE users SET day_volume = 0')
        self.connection.commit()
        print("Суточный объем сброшен для всех пользователей.")
        # Планируем следующий сброс
        self.schedule_next_reset()

    def add_reklama(self, title, href, inline_title):
        self.cursor.execute(
            'INSERT INTO admin_reklams (title, href, inline_title) VALUES (?, ?, ?)',
            (title, href, inline_title)
        )
        self.connection.commit()

    def get_all_reklams(self):
        self.cursor.execute(
            'SELECT * FROM admin_reklams'
        )
        result = self.cursor.fetchall()
        return result if result else None

    def remove_reklam(self, title):
        self.cursor.execute(
            'DELETE FROM admin_reklams WHERE title= ?', (title,)
        )
        self.connection.commit()

    def add_or_rm_bot_stop(self, prohibiting_user_id,
                                 prohibiting_username,
                                 prohibiting_user_first_name,
                                 prohibited_user_id,
                                 prohibited_username,
                                 prohibited_user_first_name
                           ):
        self.add_user(user_id=prohibiting_user_id,
                      user_name=prohibiting_username,
                      first_name=prohibiting_user_first_name)

        self.add_user(user_id=prohibited_user_id,
                      user_name=prohibited_username,
                      first_name=prohibited_user_first_name)

        self.cursor.execute(
            'SELECT bot_stop_protection FROM users WHERE user_id = ?', (prohibited_user_id,)
        )
        is_protective = self.cursor.fetchone()

        is_bot_stop = self.get_reply_permissions(prohibiting_user_id, prohibited_user_id)
        if is_protective[0] == 0:
            if is_bot_stop == "разрешено":
                try:
                    self.cursor.execute(
                        'INSERT INTO users_bot_stop (prohibiting_user_id, prohibited_user_id) VALUES (?, ?)',
                        (prohibiting_user_id, prohibited_user_id)
                    )
                    self.connection.commit()
                    print("Бот стоп добавлен")
                    return "Бот стоп добавлен"

                except sqlite3.IntegrityError:
                    self.cursor.execute(
                        'DELETE FROM users_bot_stop WHERE prohibiting_user_id = ? AND prohibited_user_id = ?',
                        (prohibiting_user_id, prohibited_user_id)
                    )
                    self.connection.commit()
                    print("Бот стоп убран")
                    return "Бот стоп убран"

            else:
                self.cursor.execute(
                    'DELETE FROM users_bot_stop WHERE prohibiting_user_id = ? AND prohibited_user_id = ?',
                    (prohibiting_user_id, prohibited_user_id)
                )
                self.connection.commit()
                print("Бот стоп убран")
                return "Бот стоп убран"
        else:
            return "защита"

    def set_protection(self, user_id):
        self.cursor.execute(
            'UPDATE users SET bot_stop_protection = ? WHERE user_id = ?', (True, user_id)
        )
        self.cursor.execute(
            'DELETE FROM users_bot_stop WHERE prohibited_user_id = ?', (user_id,)
        )
        self.connection.commit()
        return True

    def get_reply_permissions(self, user_id, reply_user_id):
        self.cursor.execute(
            'SELECT * FROM users_bot_stop WHERE prohibiting_user_id = ? AND prohibited_user_id = ?',
            (reply_user_id, user_id)
        )
        result = self.cursor.fetchone()
        print(result)
        if result is None:
            return "разрешено"

        elif result[1] == user_id and result[0] == reply_user_id:
            return "запрещено"
