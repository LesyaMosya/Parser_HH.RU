import re
import requests
from bs4 import BeautifulSoup
import pymysql


def checkStringWage(stringWage):
    patternSearchRusLetters = r'[^0-9+–+A-Z]'
    stringWage = re.sub(patternSearchRusLetters, "", stringWage)

    patternUSD = r'USD'
    matchUSD = re.search(patternUSD, stringWage)
    patternEUR = r'EUR'
    matchEUR = re.search(patternEUR, stringWage)
    patternInterval = r'–'
    matchInterval = re.search(patternInterval, stringWage)

    stringWage = searchNumbers(stringWage)
    if matchInterval is not None:
        stringWage = calculateSalaryRange(stringWage)
    else:
        stringWage = float(stringWage[0])
    if matchEUR is not None:
        stringWage = convertEUR(stringWage)
    if matchUSD is not None:
        stringWage = convertUSD(stringWage)
    return stringWage


def calculateSalaryRange(salaryRange):
    salaryFrom = int(salaryRange[0])
    salaryTo = int(salaryRange[1])
    salary = (salaryFrom + salaryTo) / 2
    salary = round(salary, 0)
    return salary


def searchNumbers(salaryRange):
    patternSearchNumber = r'\d{1,}'
    salaryRange = re.findall(patternSearchNumber, salaryRange)
    return salaryRange


def convertUSD(salaryUSD):
    salaryUSD *= 74.71
    salaryUSD = round(salaryUSD, 0)
    return salaryUSD


def convertEUR(salaryEUR):
    salaryEUR *= 79.57
    salaryEUR = round(salaryEUR, 0)
    return salaryEUR


url = 'https://spb.hh.ru/vacancies/programmist?page=0'
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/74.0.3729.169 Safari/537.36'}
params = {'page': 0}
lastPage = 2

sumSalary = 0
countVacancies = 0

while params['page'] < lastPage:
    response = requests.get(url, params=params, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    wages = soup.find_all('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})
    for step in range(0, len(wages)):
        wage = wages[step].text
        checkStringWage(wage)
        sumSalary += checkStringWage(wage)
        countVacancies += 1

    listPages = soup.find_all('a', attrs={'data-qa': 'pager-page'})
    lastPage = int(listPages.pop().text)
    params['page'] += 1

avgSalary = int(sumSalary / countVacancies)
print("Средняя зарплата по вакансии: " + str(avgSalary) + " рублей")


def mySQLConnect():
    # To connect MySQL database
    try:
        connection = pymysql.connect(
            host='localhost',
            user='LESYA-S-POLESYA/vaska',
            # password="pass",
            db='Salary_HH',
        )
        print("Successfully connected...")
        print("#" * 20)
        try:
            with connection.cursor() as cursor:
                insert_query = "INSERT INTO `Avg_Salary` (Date, Salary) VALUES (date.today(), avgSalary);"
                cursor.execute(insert_query)
                connection.commit()
        finally:
            connection.close()
    except Exception as ex:
        print("Connection refused...")
        print(ex)


mySQLConnect()
