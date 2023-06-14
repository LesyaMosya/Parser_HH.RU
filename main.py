import re
import requests
from bs4 import BeautifulSoup

url = 'https://spb.hh.ru/vacancies/programmist'

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ''AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/108.0.0.0 ' 'YaBrowser/23.5.2.625 ' 'Yowser/2.5 ' 'Safari/537.36'}
params = {'page': 0}
pages = 1

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
    response = requests.get(url, params=params, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    countVacancies = soup.find_all("span", {'data-qa': 'vacancies-total-found'})

    patternCountVacancies = r'[^0-9]'
    countVacancies = int(re.sub(patternCountVacancies, "", countVacancies[0].text))

    wages = soup.find_all("span", {'data-qa': 'vacancy-serp__vacancy-compensation'})
    for step in range(0, len(wages)):
        wage = wages[step].text
        CheckStringWage(wage)
        sumSalary += CheckStringWage(wage)
        count += 1

    pages = int(soup.find_all("a", {'data-qa': 'pager-page'})[-1].text)
    params['page'] += 1

avgSalary = int(sumSalary / count)
print("Средняя зарплата по вакансии: " + str(avgSalary) + " рублей")
