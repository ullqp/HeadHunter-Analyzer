import os
from dotenv import load_dotenv

from hh_api import HHApi
from db import DBManager

load_dotenv()

db_config = {
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': os.getenv('POSTGRES_HOST'),
    'port': os.getenv('POSTGRES_PORT'),
    'dbname': os.getenv('POSTGRES_DB')
}

def main():
    # Список с работодателями
    employers = [84585, 2624085, 625332, 66989, 80, 4181, 4233, 3388, 2460946, 1740, 15478]

    db = DBManager(
        host=db_config["host"],
        user=db_config["user"],
        password=db_config["password"],
        port=db_config["port"],
        db_name=db_config['dbname']
    )

    for i in employers:
        employer, vacancies = HHApi.get_info_about_employer(i)

        db.add_employer(employer)
        employer_id = db.total_employers()
        for vacancy in vacancies:
            vacancy["employer_id"] = employer_id
            db.add_vacancy(vacancy)

    print(db.get_companies_and_vacancies_count())
    print(db.get_all_vacancies())
    print(db.get_avg_salary())
    print(db.get_vacancies_with_higher_salary())
    print(db.get_vacancies_with_keyword("python"))

if __name__ == "__main__":
    main()