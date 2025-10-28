# Проект по работе с базой данных вакансий с hh.ru

Этот проект предназначен для сбора данных о компаниях и вакансиях с сайта hh.ru, их хранения в базе данных PostgreSQL и предоставления удобного интерфейса для работы с этими данными.

## Функциональность проекта

- Получение данных о работодателях и вакансиях через API hh.ru
- Создание структуры базы данных PostgreSQL для хранения информации
- Загрузка данных в базу данных
- Класс для управления данными с различными методами фильтрации и анализа


## Установка и настройка

### Предварительные требования

- Python 3.7+
- PostgreSQL
- Учетная запись на hh.ru (для API)

### Установка и настройка

```bash
pip install -r requirements.txt

python main.py
```
# Примеры использования DBManager
from src.db_manager import DBManager

## Создание экземпляра менеджера БД
db_manager = DBManager()

## Получение списка компаний и количества вакансий
companies = db_manager.get_companies_and_vacancies_count()

## Получение всех вакансий
vacancies = db_manager.get_all_vacancies()

## Получение средней зарплаты
avg_salary = db_manager.get_avg_salary()

## Поиск вакансий с высокой зарплатой
high_salary_vacancies = db_manager.get_vacancies_with_higher_salary()

## Поиск вакансий по ключевому слову
python_vacancies = db_manager.get_vacancies_with_keyword('python')

# Структура базы данных
## Таблица companies

id SERIAL PRIMARY KEY

company_id INTEGER UNIQUE - ID компании из hh.ru

name VARCHAR(255) - Название компании

url VARCHAR(255) - Ссылка на компанию

description TEXT - Описание компании

## Таблица vacancies

id SERIAL PRIMARY KEY

vacancy_id INTEGER UNIQUE - ID вакансии из hh.ru

company_id INTEGER REFERENCES companies(company_id)

title VARCHAR(255) - Название вакансии

salary_from INTEGER - Нижняя граница зарплаты

salary_to INTEGER - Верхняя граница зарплаты

currency VARCHAR(10) - Валюта зарплаты

url VARCHAR(255) - Ссылка на вакансию

description TEXT - Описание вакансии

experience VARCHAR(100) - Требуемый опыт



# Лицензия
Этот проект создан в учебных целях.
