import requests
from time import sleep
from dotenv import load_dotenv
import os
import terminaltables
from itertools import count


DEFAULT_AREA_ID = 1
DEFAULT_CITY = 'Москва'


def calculate_salary(salary_from, salary_to):
    if not salary_from:
        middle_salary = salary_to * 0.8
    elif not salary_to:
        middle_salary = salary_from * 1.2
    else:
        middle_salary = (salary_to + salary_from) / 2
    return middle_salary


def predict_salary_hh(salary):
    if not salary:
        return None
    return calculate_salary(salary['from'], salary['to'])


def predict_salary_sj(salary_from, salary_to):
    if salary_from and salary_to:
        return calculate_salary(salary_from, salary_to)
    return 0


def predict_rub_salary_hh(programming_languages):
    avg_vacancy_salary = {}
    for programming_language in programming_languages:
        avg_vacancy_salary[programming_language] = {}
        url = 'https://api.hh.ru/vacancies'
        middle_salaries = []
        params = {
            'text': f'Программист {programming_language}',
            'area': DEFAULT_AREA_ID
        }
        for page in count(0):
            sleep(1)
            response = requests.get(url, params=params)
            response.raise_for_status()
            api_response_content = response.json()
            params['page'] = page
            for vacancy in api_response_content['items']:
                middle_salary = predict_salary_hh(vacancy.get('salary'))
                if middle_salary:
                    middle_salaries.append(middle_salary)
            if page >= api_response_content['pages']:
                break
        avg_vacancy_salary[programming_language] = {
                'average_salary': int(sum(middle_salaries) / len(middle_salaries)) if middle_salaries else 0,
                'vacancies_found': api_response_content['found'],
                'vacancies_processed': len(middle_salaries)
            }
    return avg_vacancy_salary


def predict_rub_salary_sj(token, programming_languages):
    avg_vacancy_salary = {}

    for programming_language in programming_languages:
        avg_vacancy_salary[programming_language] = {}

        superjob_url = 'https://api.superjob.ru/2.0/vacancies'
        headers = {
            'X-Api-App-Id': token
        }

        params = {
            'keyword': f'Программист {programming_language}',
            'town': DEFAULT_CITY,
            'count': 100
        }

        vacancies_sj = []

        for page in count(0):
            params['page'] = page
            try:
                response = requests.get(superjob_url, headers=headers, params=params, timeout=60)
                response.raise_for_status()
                response = response.json()
            except requests.exceptions.HTTPError as ex:
                if response.status_code == 400:
                    print(f"Bad request occurred. Exiting pagination loop for {programming_language}.")
                    break
                else:
                    raise ex

            response_objects = response.get('objects', [])
            vacancies_sj.extend(response_objects)

            if not response.get('more'):
                break

        middle_salaries = []
        for vacancy in vacancies_sj:
            if not vacancy:
                continue
            middle_salary = int(predict_salary_sj(vacancy['payment_from'], vacancy['payment_to']))
            if middle_salary:
                middle_salaries.append(middle_salary)
                
        if middle_salaries:
            try:
                avg_salary = int(sum(middle_salaries) / len(middle_salaries))
            except ZeroDivisionError:
                avg_salary = None

            avg_vacancy_salary[programming_language] = {
                'average_salary': avg_salary,
                'vacancies_found': len(vacancies_sj),
                'vacancies_processed': len(middle_salaries),
            }
        else:
            avg_vacancy_salary[programming_language] = {
                'vacancies_found': len(vacancies_sj)
            }

    return avg_vacancy_salary

def create_table(processed_information, title):
    table_data = [
        ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']
    ]
    for language, stats in processed_information.items():
        vacancies_found = stats.get('vacancies_found', 0)
        vacancies_processed = stats.get('vacancies_processed', 0)
        average_salary = stats.get('average_salary', 0)
        
        table_data.append([language, vacancies_found, vacancies_processed, average_salary])

    table = terminaltables.AsciiTable(table_data)
    table.title = title
    return table.table


if __name__ == '__main__':
    load_dotenv()
    token = os.getenv('SJ_SECRET_KEY')
    programming_languages = ['Python', 'Java', 'C++', 'JavaScript']
    # print(create_table(predict_rub_salary_hh(programming_languages), 'hh'))
    print(create_table(predict_rub_salary_sj(token, programming_languages), 'sj'))
