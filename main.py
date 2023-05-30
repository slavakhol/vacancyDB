# Список выбранных компаний и их ID на сайте HH
#
# 1740 Яндекс
# 3529 Сбер
# 15478 VK
# 78638 Тинькофф
# 740 Норильский никель
# 3388 Газпромбанк
# 23186 Русагро
# 3776 МТС Диджитал
# 6041 Северсталь
# 4233 X5 Group
# 2180 Ozon

import os
import requests
import psycopg2
from DBmanager import DBmanager

def main():
    #Создаем новую базу данных для работы с проектом
    try:
        conn = psycopg2.connect(user="postgres", password=os.getenv('PASSWORD'))
        with conn.cursor() as cursor:
            conn.autocommit = True
            cursor.execute("CREATE DATABASE vacancydb")
        conn.close()
    except:
        pass

    #Обращаемся по API HH и получаем список вакансий по заданным компаниям
    response = requests.get(
        "https://api.hh.ru/vacancies?",
        headers={"HH-User-Agent": 'VacancyMachine/1.0 (slava.kholopov@gmail.com)'},
        params={"employer_id": (1740, 3529, 15478, 78638, 740, 3388, 23186, 3776, 6041, 4233, 2180), "per_page": 100}
    )
    #создаем структуру БД и записываем в нее полученные от HH данные
    with psycopg2.connect(database="vacancydb", user="postgres", password=os.getenv('PASSWORD')) as conn:


        with conn.cursor() as cursor:
            cursor.execute(
                "CREATE TABLE employers(employer_id int PRIMARY KEY NOT NULL, company_name varchar(255), url varchar(255));")
            cursor.execute("CREATE TABLE vacancies(vacancy_id int PRIMARY KEY NOT NULL, salary_from int, salary_to int, title varchar(255), url varchar(255), employer_id int REFERENCES employers(employer_id))")
            for item in response.json()['items']:
                if item['salary'] is None:
                    salary_from = 0
                    salary_to = 0
                else:
                    salary_from = item['salary']['from']
                    salary_to = item['salary']['to']
                if salary_from == None:
                    salary_from = 0
                if salary_to == None:
                    salary_to = 0

                cursor.execute(
                    "INSERT INTO employers (employer_id, company_name, url) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                    (item['employer']['id'], item['employer']['name'], item['employer']['alternate_url']))

                cursor.execute("INSERT INTO vacancies (vacancy_id, salary_from, salary_to, title, url, employer_id) VALUES (%s, %s, %s, %s, %s, %s)",
                    (item['id'], salary_from, salary_to, item['name'], item['alternate_url'], item['employer']['id']))



    # Итерация с пользователем по функционалу класса DBmanager
    print("Что вы хотите сделать со списком вакансий?\n"
          "1 - Получить спсиок всех компаний и узнать количество вакансий у каждой компании? \n"
          "2 - Получить список всех вакансий с указанием названия компании, названия вакансии и зарплаты и ссылки на вакансию\n"
          "3 - Получить среднюю зарплату по вакансиям\n"
          "4 - Получить список всех вакансий, у которых зарплата выше средней по всем вакансиям.\n"
          "Получить список всех вакансий по ключевому слову - введите ключевое слово\n")

    choice = input("Введите значение или клюечвое слово:")


    if choice == '1':
        for row in DBmanager('vacancydb').get_companies_and_vacancies_count():
            print(f"{row[0]} - {row[1]} вакансий")
    elif choice == '2':
        for row in DBmanager('vacancydb').get_all_vacancies():
            if row[1] == 0 and row[2] == 0:
                    salary = "Зарплата не указана."
            elif row[1] == 0 and row[2] != 0:
                salary = "Зарплата до " + str(row[2]) + " руб."
            elif row[1] != 0 and row[2] == 0:
                salary = "Зарплата от " + str(row[1]) + " руб."
            else:
                salary = "Зарплата от " + str(row[1])+ " до " + str(row[2]) + "  руб."

            print(f"{row[0]}. {salary} Ссылка: {row[3]} Компания: {row[4]}")
    elif choice == '3':
        print(f"Средняя зарплата по вакансиям составляет {int(DBmanager('vacancydb').get_avg_salary())} руб.")
    elif choice == '4':
            for row in DBmanager('vacancydb').get_vacancies_with_higher_salary():
                if row[1] == 0 and row[2] == 0:
                    salary = "Зарплата не указана."
                elif row[1] == 0 and row[2] != 0:
                    salary = "Зарплата до " + str(row[2]) + " руб."
                elif row[1] != 0 and row[2] == 0:
                    salary = "Зарплата от " + str(row[1]) + " руб."
                else:
                    salary = "Зарплата от " + str(row[1]) + " до " + str(row[2]) + "  руб."

                print(f"{row[0]}. {salary} Ссылка: {row[3]} Компания: {row[4]}")
    else:
        for row in DBmanager('vacancydb').get_vacancies_with_keyword(choice):
            if row[1] == 0 and row[2] == 0:
                    salary = "Зарплата не указана."
            elif row[1] == 0 and row[2] != 0:
                salary = "Зарплата до " + str(row[2]) + " руб."
            elif row[1] != 0 and row[2] == 0:
                salary = "Зарплата от " + str(row[1]) + " руб."
            else:
                salary = "Зарплата от " + str(row[1])+ " до " + str(row[2]) + "  руб."

            print(f"{row[0]}. {salary} Ссылка: {row[3]} ")

if __name__ == '__main__':
    main()


