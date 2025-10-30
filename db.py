import psycopg2
from typing import List, Tuple, Optional, Dict, Any


class DBManager:
    """Класс для управления базой данных вакансий и работодателей."""
    
    def __init__(self, host: str, user: str, password: str, 
                 port: str, db_name: str) -> None:
        """
        Инициализация менеджера базы данных.
        
        Параметры:
            host: Хост базы данных
            user: Имя пользователя
            password: Пароль пользователя
            port: Порт подключения
            db_name: Название базы данных
        """
        
        self.db_info = {
            "host": host,
            "user": user,
            "password": password,
            "port": port,
            "db_name": db_name
        }
        
        self.create_database(self.db_info["db_name"])
        self.connect()
        
        self.create_employers_table()
        self.create_vacancies_table()

    def connect(self) -> None:
        self.conn = psycopg2.connect(
            dbname=self.db_info["db_name"], 
            user=self.db_info["user"], 
            password=self.db_info["password"], 
            host=self.db_info["host"], 
            port=self.db_info["port"]
        )
        self.cur = self.conn.cursor()

    def create_database(self, db_name: str) -> None:
        """
        Создание новой базы данных.
        
        Параметры:
            db_name: Название базы данных
        """
        conn = psycopg2.connect(
            dbname="postgres",
            user=self.conn.info.user,
            password=self.conn.info.password,
            host=self.conn.info.host,
            port=self.conn.info.port
        )
        cur = conn.cursor()
        
        cur.execute(f"CREATE DATABASE {db_name}")
        conn.commit()
        
        cur.close()
        conn.close()

    def create_employers_table(self) -> None:
        """Создание таблицы работодателей, если она не существует."""
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS employers (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                url TEXT UNIQUE
            );
        """)
        self.conn.commit()

    def create_vacancies_table(self) -> None:
        """Создание таблицы вакансий, если она не существует."""
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS vacancies (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                url TEXT UNIQUE,
                employer_id INTEGER REFERENCES employers(id),
                salary INTEGER
            );
        """)
        self.conn.commit()

    def total_employers(self) -> int:
        """
        Получение общего количества работодателей в базе данных.
        
        Возвращает:
            Количество работодателей
        """
        self.cur.execute("SELECT COUNT(*) FROM employers")
        result = self.cur.fetchone()
        return result[0] if result else 0

    def add_employer(self, item: Dict[str, Any]) -> None:
        """
        Добавление нового работодателя в базу данных.
        
        Параметры:
            item: Словарь с данными работодателя, содержащий ключи:
                - name: Название работодателя
                - url: URL работодателя
        """
        try:
            self.cur.execute(
                """
                INSERT INTO employers (name, url)
                VALUES (%s, %s)
                ON CONFLICT (url) DO NOTHING;
                """,
                (item["name"], item["url"])
            )
            self.conn.commit()
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"Ошибка при добавлении работодателя: {e}")

    def add_vacancy(self, item: Dict[str, Any]) -> None:
        """
        Добавление новой вакансии в базу данных.
        
        Параметры:
            item: Словарь с данными вакансии, содержащий ключи:
                - name: Название вакансии
                - url: URL вакансии
                - employer_id: ID работодателя
                - salary: Зарплата
        """
        try:
            self.cur.execute(
                """
                INSERT INTO vacancies (name, url, employer_id, salary)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (url) DO NOTHING;
                """,
                (item["name"], item["url"], item["employer_id"], item["salary"])
            )
            self.conn.commit()
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"Ошибка при добавлении вакансии: {e}")

    def get_companies_and_vacancies_count(self) -> List[Tuple]:
        """
        Получение списка компаний с количеством вакансий.
        
        Возвращает:
            Список кортежей в формате (название_компании, количество_вакансий),
            отсортированный по убыванию количества вакансий
        """
        self.cur.execute("""
            SELECT e.name, COUNT(v.id) as vacancies_count
            FROM employers e
            LEFT JOIN vacancies v ON e.id = v.employer_id
            GROUP BY e.id, e.name
            ORDER BY vacancies_count DESC;
        """)
        return self.cur.fetchall()

    def get_all_vacancies(self) -> List[Tuple]:
        """
        Получение списка всех вакансий с подробной информацией.
        
        Возвращает:
            Список кортежей в формате:
            (название_компании, название_вакансии, зарплата, ссылка_на_вакансию)
        """
        self.cur.execute("""
            SELECT e.name, v.name, v.salary, v.url
            FROM vacancies v
            INNER JOIN employers e ON v.employer_id = e.id
            ORDER BY v.salary DESC NULLS LAST;
        """)
        return self.cur.fetchall()

    def get_avg_salary(self) -> float:
        """
        Расчет средней зарплаты по всем вакансиям.
        
        Возвращает:
            Средняя зарплата (округленная до целого числа)
        """
        self.cur.execute("""
            SELECT ROUND(AVG(salary)) as avg_salary
            FROM vacancies
            WHERE salary IS NOT NULL;
        """)
        result = self.cur.fetchone()
        return result[0] if result else 0.0

    def get_vacancies_with_higher_salary(self) -> List[Tuple]:
        """
        Получение вакансий с зарплатой выше средней.
        
        Возвращает:
            Список вакансий с зарплатой выше средней
        """
        avg_salary = self.get_avg_salary()
        self.cur.execute("""
            SELECT *
            FROM vacancies
            WHERE salary > %s
            ORDER BY salary DESC;
        """, (avg_salary,))
        return self.cur.fetchall()

    def get_vacancies_with_keyword(self, keyword: str) -> List[Tuple]:
        """
        Поиск вакансий по ключевому слову в названии.
        
        Параметры:
            keyword: Ключевое слово для поиска
            
        Возвращает:
            Список вакансий, содержащих ключевое слово в названии
        """
        self.cur.execute("""
            SELECT *
            FROM vacancies
            WHERE name ILIKE %s
            ORDER BY salary DESC NULLS LAST;
        """, (f'%{keyword}%',))
        return self.cur.fetchall()

    def close_connection(self) -> None:
        """Закрытие соединения с базой данных."""
        self.cur.close()
        self.conn.close()

    def __exit__(self) -> None:
        """Закрытие соединения при выходе."""
        self.close_connection()
