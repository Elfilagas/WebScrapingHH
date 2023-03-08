import requests
from bs4 import BeautifulSoup
from fake_headers import Headers
import json


HOST = "https://spb.hh.ru"
VACANCIES = f"{HOST}/search/vacancy?text=python&area=1&area=2"
# Вариант 2. С ключевыми словами в запросе реже блокируется НН, но судя по заданию так нельзя делать
# VACANCIES = f"{HOST}/search/vacancy?text=python+django+flask&area=1&area=2"


def get_headers():
    """Form headers for requests"""
    return Headers(browser="chrome", os="win").generate()


def get_text(url):
    """Get raw text from requests"""
    return requests.get(url, headers=get_headers()).text


def parse_article(vacancy_tag) -> dict:
    """Parse text and extract needed information"""
    link_tag = vacancy_tag.find("a", class_="serp-item__title")
    salary = vacancy_tag.find("span", attrs={'data-qa': "vacancy-serp__vacancy-compensation"})
    salary = salary.text if salary else "Не указана"
    company = vacancy_tag.find("a", attrs={'data-qa': "vacancy-serp__vacancy-employer"}).text
    city = vacancy_tag.find("div", attrs={'data-qa': "vacancy-serp__vacancy-address"}).text.split(',')[0]
    link = link_tag["href"]
    return {
        "link": link,
        "salary": salary,
        "company": company,
        "city": city,
    }


def parse_page(page_num, only_usd=False) -> list:
    html = get_text(f"{VACANCIES}&page={page_num}")
    soup = BeautifulSoup(html, features="html5lib")
    vacancies = soup.find(attrs={'data-qa': 'vacancy-serp__results'}).find_all(class_="serp-item")
    vacancies_parsed = []
    for vacancy in vacancies:
        parsed = parse_article(vacancy)
        if only_usd:
            if not ('USD' in parsed['salary']):
                continue
        # Если используем Вариант 2, то получение description и проверка не нужны, что ускрорит обработку
        description = get_text(parsed['link'])
        if 'Django' in description and 'Flask' in description:
            vacancies_parsed.append(parsed)
    return vacancies_parsed


if __name__ == "__main__":
    search_only_USD = False
    if input("Искать только вакансии в USD (да/нет): ") == 'да':
        search_only_USD = True
    print("Поиск вакансий...")
    result = []
    for page in range(40):
        print(f"Обработка страницы {page + 1} из 40")
        result.extend(parse_page(page, search_only_USD))
    print(f"Найдено вакансий {len(result)} шт.")
    print("Запись в файл 'result.json'")
    with open('result.json', 'w', encoding='utf-8') as file:
        json.dump(result, file, ensure_ascii=False, indent=4)
