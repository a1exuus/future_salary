import requests
from time import sleep
from dotenv import load_dotenv
import os
import terminaltables
from itertools import count


def calculate_salary(salary_from, salary_to):
    if salary_from == 0 or not salary_from:
        middle_salary = salary_to * 0.8
    elif salary_to == 0 or not salary_to:
        middle_salary = salary_from * 1.2
    else:
        middle_salary = (salary_to + salary_from) / 2
    return middle_salary


def predict_salary_hh(salary):
    if not salary:
        return None
    return calculate_salary(salary['from'], salary['to'])


def predict_salary_sj(salary_from, salary_to):
    if salary_from is not None and salary_to is not None:
        return calculate_salary(salary_from, salary_to)
    return 0



def predict_rub_salary_hh(programming_languages):
    avg_vacancy_salary = {}
    vacancies_found = 0
    vacancies_processed = 0
    for programming_language in programming_languages:
        avg_vacancy_salary[programming_language] = {}
        url = 'https://api.hh.ru/vacancies'
        middle_salaries = []
        params = {
            'text': f'Программист {programming_language}',
            'area': 1
                   }
        for page in count(0):
            sleep(1)
            response = requests.get(url, params=params)
            response.raise_for_status()
            response_data = response.json()
            params['page'] = page
            for vacancy in response_data['items']:
                vacancies_found += 1
                middle_salary = predict_salary_hh(vacancy.get('salary'))
                if middle_salary:
                    vacancies_processed += 1
                    middle_salaries.append(middle_salary)
            if page >= response_data['pages']:
                break
        avg_vacancy_salary[programming_language]['average_salary'] = int(sum(middle_salaries) / len(middle_salaries))
        avg_vacancy_salary[programming_language]['vacancies_found'] = vacancies_found
        avg_vacancy_salary[programming_language]['vacancies_processed'] = vacancies_processed
    return avg_vacancy_salary


def predict_rub_salary_sj(token, programming_languages):
    avg_vacancy_salary = {}
    vacancies_found = 0
    vacancies_processed = 0
    for programming_language in programming_languages:
        avg_vacancy_salary[programming_language] = {}
        url = 'https://api.superjob.ru/2.0/vacancies'
        headers = {
            'X-Api-App-Id': token
        }
        params = {
            'keyword': f'Программист {programming_language}',
            'town': 'Москва',
            'count': 500
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        response = response.json()
        response_objects = response.get('objects')
        middle_salaries = []
        for vacancy in response_objects:
            if not vacancy:
                continue
            middle_salary = int(predict_salary_sj(vacancy['payment_from'], vacancy['payment_to']))
            if middle_salary != 0:
                vacancies_processed += 1
                middle_salaries.append(middle_salary)
            vacancies_found += 1
        if middle_salaries:
            avg_vacancy_salary[programming_language]['average_salary'] = int(sum(middle_salaries) / len(middle_salaries))
            avg_vacancy_salary[programming_language]['vacancies_found'] = vacancies_found
            avg_vacancy_salary[programming_language]['vacancies_processed'] = vacancies_processed
    return avg_vacancy_salary


def create_table_sj(processed_information):
    table_data = [
        ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']
    ]
    information_keys = list(processed_information.keys())
    for key in information_keys:
        data = [key, processed_information[key]['vacancies_found'], processed_information[key]['vacancies_processed'], processed_information[key]['average_salary']]
        table_data.append(data)
    table = terminaltables.AsciiTable(table_data)
    table.title = 'SuperJob Moscow'
    return table.table


def create_table_hh(processed_information):
    table_data = [
        ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']
    ]
    information_keys = list(processed_information.keys())
    for key in information_keys:
        data = [key, processed_information[key]['vacancies_found'], processed_information[key]['vacancies_processed'], processed_information[key]['average_salary']]
        table_data.append(data)
    table = terminaltables.AsciiTable(table_data)
    table.title = 'HeadHunter Moscow'
    return table.table

if __name__ == '__main__':
    load_dotenv()
    token = os.getenv('SJ_SECRET_KEY')
    programming_languages = ['Python', 'Java', 'C++', 'JavaScript']
    # print(create_table_hh(predict_rub_salary_hh(programming_languages)))
    print(create_table_sj(predict_rub_salary_sj(token ,programming_languages)))