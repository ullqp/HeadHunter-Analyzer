from locale import currency
import requests

class HHApi:
    """Класс для работы с API HH.ru"""

    @staticmethod
    def get_area_by_locale(
        locale: str = "RU"
    ):
        """
        Получение id зоны по локали

        Параметры:
            locale: Локаль
        """

        req = requests.get(
            url="https://api.hh.ru/areas",
            params={
                "locale":locale
            }
        )

        return req.json()

    @staticmethod
    def get_employers(
        text="",
        area="113"
    ):
        """
        Поиск работодателей

        Параметры:
            text: Текст для поиска
            area: Id зоны поиска, по умолчанию - Россия
        """

        req = requests.get(
            url="https://api.hh.ru/employers",
            params = {
                "text": text,
                "area": area
            }
        )

        return req.json()

    @staticmethod
    def get_info_about_employer(
        employer_id: str    
    ):
        """
        Получение информации о работодателе и его вакансиях

        Параметры:
            employer_id: Id работодателя
        """

        employer = requests.get(
            url=f"https://api.hh.ru/employers/{employer_id}"
        ).json()

        vacancies = requests.get(
            url=employer["vacancies_url"]+"&per_page=100"
        ).json()

        employer_formated = {
            "name": employer["name"],
            "url": employer["alternate_url"]
        }

        vacancies_formated = []

        for vacancy in vacancies["items"]:

            salary = None
            currency = None

            if vacancy.get("salary") is not None:
                currency = vacancy["salary"].get("currency")

                _from = vacancy["salary"].get("from")
                _to = vacancy["salary"].get("to")
                
                if _from is not None and _to is not None:
                    salary = (_from + _to) // 2
                else:
                    salary = _from or _to


            vacancies_formated.append({
                "name": vacancy["name"],
                "url": vacancy["alternate_url"],
                "salary": salary,
                "currency": currency
            })

        return employer_formated, vacancies_formated