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
                count INTEGER DEFAULT 0,
                volume REAL DEFAULT 0,
                attempts INTEGER DEFAULT 3,
                last_attempt_time TEXT
            );
            """
        )
        self.connection.commit()

    def add_user(self, user_id: int, user_name: str) -> None:
        try:
            # Добавление нового пользователя с начальным счетчиком 0 и тремя попытками
            self.cursor.execute(
                'INSERT INTO users (user_id, user_name, count, volume, attempts, last_attempt_time) VALUES (?, ?, ?, ?, ?, ?)',
                (user_id, user_name, 0, 0, 3, datetime.datetime.now().isoformat())
            )
            self.connection.commit()
        except sqlite3.IntegrityError:
            print(f"User with ID {user_id} or name {user_name} already exists.")

    def user_exists(self, user_id: int) -> bool:
        # Проверка, существует ли пользователь в базе данных
        result = self.cursor.execute(
            "SELECT user_id FROM users WHERE user_id = ?", (user_id,)
        )
        return result.fetchone() is not None

    def get_user(self, user_id: int = None, user_name: str = None):
        """
        Получение информации о пользователе по user_id или user_name.

        :param user_id: ID пользователя.
        :param user_name: Имя пользователя.
        :return: Кортеж (user_id, user_name, count) или None, если пользователь не найден.
        """
        if user_id is not None:
            # Получение информации по user_id
            result = self.cursor.execute(
                'SELECT user_id, user_name, count FROM users WHERE user_id = ?', (user_id,)
            )
        elif user_name is not None:
            # Получение информации по user_name
            result = self.cursor.execute(
                'SELECT user_id, user_name, count FROM users WHERE user_name = ?', (user_name,)
            )
        else:
            raise ValueError("Необходимо указать user_id или user_name.")

        row = result.fetchone()
        return row if row else None

    def check_attempt_reset(self, user_id):
        # Проверка, прошел ли час для восстановления попытки
        self.cursor.execute(
            'SELECT attempts, last_attempt_time FROM users WHERE user_id = ?', (user_id,)
        )
        result = self.cursor.fetchone()

        if result:
            attempts, last_attempt_time = result
            if attempts == 0:
                # Проверка, прошло ли больше часа с последней попытки
                last_time = datetime.datetime.fromisoformat(last_attempt_time)
                if (datetime.datetime.now() - last_time).total_seconds() >= 3600:
                    # Восстановить 1 попытку и обновить время последней попытки
                    self.cursor.execute(
                        'UPDATE users SET attempts = 1, last_attempt_time = ? WHERE user_id = ?',
                        (datetime.datetime.now().isoformat(), user_id)
                    )
                    self.connection.commit()
                    return True
        return False

    def add_volume(self, user_id, volume):
        # Сначала проверим, нужно ли восстановить попытку
        self.check_attempt_reset(user_id)

        # Проверка количества попыток пользователя
        self.cursor.execute(
            'SELECT attempts FROM users WHERE user_id = ?', (user_id,)
        )
        attempts = self.cursor.fetchone()

        if attempts and attempts[0] > 0:
            # Если попыток больше 0, добавляем объем и уменьшаем количество попыток на 1
            self.cursor.execute(
                'UPDATE users SET volume = volume + ?, attempts = attempts - 1, last_attempt_time = ? WHERE user_id = ?',
                (round(volume, 1), datetime.datetime.now().isoformat(), user_id)
            )
            self.connection.commit()
            return True
        else:
            return False

    def add_attempts(self, user_id, attempts: int = 1):
        # Увеличение количества попыток для пользователя
        self.cursor.execute(
            'UPDATE users SET attempts = attempts + ? WHERE user_id = ?', (attempts, user_id)
        )
        self.connection.commit()

    def get_volume(self, user_id):
        # Запрос на получение значения volume для указанного user_id
        self.cursor.execute(
            'SELECT volume FROM users WHERE user_id = ?', (user_id,)
        )
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_time_until_next_attempt(self, user_id):
        # Проверка времени до следующей попытки
        self.cursor.execute(
            'SELECT attempts, last_attempt_time FROM users WHERE user_id = ?', (user_id,)
        )
        result = self.cursor.fetchone()

        if result:
            attempts, last_attempt_time = result
            if attempts == 0:
                # Вычисляем разницу времени до следующей попытки
                last_time = datetime.datetime.fromisoformat(last_attempt_time)
                time_elapsed = (datetime.datetime.now() - last_time).total_seconds()
                time_left = max(3600 - time_elapsed, 0)  # Время до следующей попытки в секундах

                minutes, seconds = divmod(int(time_left), 60)
                return f"{minutes} минут {seconds}"
            else:
                return "Попытки уже доступны."
        else:
            return "Пользователь не найден."

    def get_volume_statistic(self):
        pass
