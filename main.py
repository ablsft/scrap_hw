import requests
import bs4
import fake_headers
import time
import json

headers_gen = fake_headers.Headers(browser='chrome', os='win')
vacancy_list = []
vacancy_list_usd = []
pages = 5

for page in range(1, pages+1):
    response = requests.get(f'https://hh.ru/search/vacancy?text=python&area=1&area=2&page={page}',
                            headers=headers_gen.generate())
    search_html = response.text
    search_soup = bs4.BeautifulSoup(search_html, 'lxml')

    div_vacancy_list_tag = search_soup.find('div', id='a11y-main-content')

    if div_vacancy_list_tag:
        vacancy_tags = div_vacancy_list_tag.find_all('div', class_='serp-item')

        for vacancy_tag in vacancy_tags:
            vacancy_link_tag = vacancy_tag.find('a', class_='serp-item__title')
            vacancy_link = vacancy_link_tag['href']
            
            time.sleep(0.1)
            response_vacancy = requests.get(vacancy_link, headers=headers_gen.generate())
            response_vacancy_html = response_vacancy.text
            response_vacancy_soup = bs4.BeautifulSoup(response_vacancy_html, features='lxml')
            vacancy_description = response_vacancy_soup.find('div', class_='g-user-content')
            vacancy_description_search = str(vacancy_description).lower()

            if 'django' in vacancy_description_search and 'flask' in vacancy_description_search:
                salary = ''
                city = ''

                vacancy_title_tag = response_vacancy_soup.find('div', class_='vacancy-title')
                salary_tag = vacancy_title_tag.find('span', class_='bloko-header-section-2')
                if salary_tag:
                    salary = salary_tag.text.replace(u'\xa0', u'')

                company_tag = response_vacancy_soup.find('div', class_='vacancy-company-redesigned')
                company_name = company_tag.span.a.span.text.replace(u'\xa0', u' ')
                if company_tag.p:
                    city = company_tag.p.text
                elif company_tag.a:
                    city_tag = company_tag.find('a', class_='bloko-link_disable-visited')
                    city = city_tag.span.text.split(',')[0]

                vacancy_dict = {
                    'link': vacancy_link,
                    'salary': salary,
                    'company_name': company_name,
                    'city': city
                }

                print(vacancy_dict)

                vacancy_list.append(vacancy_dict)
                if '$' in vacancy_dict['salary']:
                    vacancy_list_usd.append(vacancy_dict)
            
with open('vacancies.json', 'w', encoding='utf-8') as f:
    json.dump(vacancy_list, f, indent=2, ensure_ascii=False)

with open('vacancies_usd.json', 'w', encoding='utf-8') as f:
    json.dump(vacancy_list_usd, f, indent=2, ensure_ascii=False)