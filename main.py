import re
import requests
from bs4 import BeautifulSoup

url = 'https://spb.hh.ru/vacancies/programmist?hhtmFromLabel=rainbow_profession&hhtmFrom=main'

params = {'page': 0}
pages = 2

sumSalary = 0
countVacancies = 0
count = 0


def CheckStringWage(stringWage):
    patternSearchRusLetters = r'[^0-9+–+A-Z]'
    stringWage = re.sub(patternSearchRusLetters, "", stringWage)

    patternUSD = r'USD'
    matchUSD = re.search(patternUSD, stringWage)
    patternEUR = r'EUR'
    matchEUR = re.search(patternEUR, stringWage)
    patternInterval = r'–'
    matchInterval = re.search(patternInterval, stringWage)

    stringWage = SearchNumbers(stringWage)
    if matchInterval is not None:
        stringWage = CalculateSalaryRange(stringWage)
    else:
        stringWage = float(stringWage[0])
    if matchEUR is not None:
        stringWage = ConvertEUR(stringWage)
    if matchUSD is not None:
        stringWage = ConvertUSD(stringWage)
    return stringWage


def CalculateSalaryRange(salaryRange):
    salaryFrom = int(salaryRange[0])
    salaryTo = int(salaryRange[1])
    salary = (salaryFrom + salaryTo) / 2
    salary = round(salary, 0)
    return salary


def SearchNumbers(salaryRange):
    patternSearchNumber = r'\d{1,}'
    salaryRange = re.findall(patternSearchNumber, salaryRange)
    return salaryRange


def ConvertUSD(salaryUSD):
    salaryUSD *= 74.71
    salaryUSD = round(salaryUSD, 0)
    return salaryUSD


def ConvertEUR(salaryEUR):
    salaryEUR *= 79.57
    salaryEUR = round(salaryEUR, 0)
    return salaryEUR


while params['page'] < pages:
    response = requests.get(url, params=params, headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                                                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                                                                       'Chrome/108.0.0.0 '
                                                                       'YaBrowser/23.1.1.1138 '
                                                                       'Yowser/2.5 '
                                                                       'Safari/537.36'})
    soup = BeautifulSoup(response.text, "html.parser")
    wages = soup.find_all('span', class_='bloko-header-section-3')

    patternCountVacancies = r'[^0-9]'
    countVacancies = int(re.sub(patternCountVacancies, "", wages[0].text))

    for step in range(1, len(wages)):
        wage = wages[step].text
        print(CheckStringWage(wage))
        sumSalary += CheckStringWage(wage)
        count += 1

    last_page_num = int(soup.find_all('a', class_='bloko-button')[-2].text)
    pages = last_page_num if pages < last_page_num else pages
    params['page'] += 1


avgSalary = sumSalary/count
print("Средняя зарплата по вакансии 'программист'")
print(avgSalary)


