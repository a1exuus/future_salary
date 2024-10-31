import requests
from time import sleep
from dotenv import load_dotenv
import os
import terminaltables


def predict_salary_hh(vacancy):
    salary = vacancy.get('salary')
    if not salary:
        return None
    if salary['from'] is None:
        middle_salary = salary['to'] * 0.8
    elif salary['to'] is None:
        middle_salary = salary['from'] * 1.2
    else:
        middle_salary = (salary['to'] + salary['from']) / 2
    return middle_salary


def predict_salary_sj(vacancy):
    salary_from, salary_to = vacancy['payment_from'], vacancy['payment_to']
    if not salary_from and salary_to:
        return None
    if salary_from == 0:
        middle_salary = salary_to * 0.8
    elif salary_to == 0:
        middle_salary = salary_from * 1.2
    else:
        middle_salary = (salary_to + salary_from) / 2
    return middle_salary


def predict_rub_salary_hh(programming_languages):
    avg_vacancy_salary = {
            programming_languages[0]: {},
            programming_languages[1]: {},
            programming_languages[2]: {},
            programming_languages[3]: {}
        }
    for programming_language in programming_languages:
        url = 'https://api.hh.ru/vacancies'
        middle_salaries = []
        response = requests.get(url, params={'text': f'Программист {programming_language}'})
        response.raise_for_status()
        try:
            pages = response.json()['pages']
            vacancies = response.json()['found']
        except:
            break
        for page in range(pages):
            sleep(1)
            response = requests.get(url, params={'page': page, 'text': f'Программист {programming_language}'})
            response.raise_for_status()
            json_response = response.json()
            for vacancy in json_response['items']:
                middle_salary = predict_salary_hh(vacancy)
                if middle_salary == None:
                    continue
                else:
                    middle_salaries.append(middle_salary)
        avg_vacancy_salary[programming_language]['average_salary'] = int(sum(middle_salaries) / len(middle_salaries))
        avg_vacancy_salary[programming_language]['vacancies_found'] = vacancies
    return avg_vacancy_salary


def predict_rub_salary_sj(token, programming_languages):
    avg_vacancy_salary = {
        programming_languages[0]: {},
        programming_languages[1]: {},
        programming_languages[2]: {},
        programming_languages[3]: {}
    }
    for programming_language in programming_languages:
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
        vacancies = 0
        for vacancy in response_objects:
            if vacancy is None:
                continue
            else:
                if predict_salary_sj(vacancy):
                    middle_salary = int(predict_salary_sj(vacancy))
                    if middle_salary == 0 or middle_salary == None:
                        continue
                    else:
                        middle_salaries.append(middle_salary)
                    vacancies += 1
        if len(middle_salaries) != 0:
            avg_vacancy_salary[programming_language]['average_salary'] = int(sum(middle_salaries) / len(middle_salaries))
            avg_vacancy_salary[programming_language]['vacancies_found'] = vacancies
    return avg_vacancy_salary


def create_table_sj(processed_information):
    information_keys = list(processed_information.keys())
    table_data = [
        ['Язык программирования', 'Вакансий найдено', 'Средняя зарплата'],
        [information_keys[0], processed_information[information_keys[0]]['vacancies_found'], processed_information[information_keys[0]]['average_salary']],
        [information_keys[1], processed_information[information_keys[1]]['vacancies_found'], processed_information[information_keys[1]]['average_salary']],
        [information_keys[2], processed_information[information_keys[2]]['vacancies_found'], processed_information[information_keys[2]]['average_salary']],
        [information_keys[3], processed_information[information_keys[3]]['vacancies_found'], processed_information[information_keys[3]]['average_salary']]
   ]
    table = terminaltables.AsciiTable(table_data)
    table.title = 'SuperJob Moscow'
    return table.table


def create_table_hh(processed_information):
    information_keys = list(processed_information.keys())
    table_data = [
        ['Язык программирования', 'Вакансий найдено', 'Средняя зарплата'],
        [information_keys[0], processed_information[information_keys[0]]['vacancies_found'], processed_information[information_keys[0]]['average_salary']],
        [information_keys[1], processed_information[information_keys[1]]['vacancies_found'], processed_information[information_keys[1]]['average_salary']],
        [information_keys[2], processed_information[information_keys[2]]['vacancies_found'], processed_information[information_keys[2]]['average_salary']],
        [information_keys[3], processed_information[information_keys[3]]['vacancies_found'], processed_information[information_keys[3]]['average_salary']]
   ]
    table = terminaltables.AsciiTable(table_data)
    table.title = 'HeadHunter Moscow'
    return table.table


if __name__ == '__main__':
    load_dotenv()
    token = os.getenv('SECRET_KEY')
    programming_languages = ['Python', 'Java', 'C++', 'JavaScript']
    print(create_table_hh(predict_rub_salary_hh(programming_languages)))
    print(create_table_sj(predict_rub_salary_sj(token ,programming_languages)))