"""
    Info from 'Finam' webpage
"""

from bs4 import BeautifulSoup
import requests

DEFAULT_URL_ARR = [
    'https://www.finam.ru/quotes/stocks/russia/?pageNumber=1',
    'https://www.finam.ru/quotes/stocks/russia/?pageNumber=2',
    'https://www.finam.ru/quotes/stocks/russia/?pageNumber=3',
    'https://www.finam.ru/quotes/stocks/russia/?pageNumber=4',
    'https://www.finam.ru/quotes/stocks/russia/?pageNumber=5',
    'https://www.finam.ru/quotes/stocks/russia/?pageNumber=6',
    'https://www.finam.ru/quotes/stocks/russia/?pageNumber=7',
    'https://www.finam.ru/quotes/stocks/russia/?pageNumber=8',
    'https://www.finam.ru/quotes/stocks/russia/?pageNumber=9',
    'https://www.finam.ru/quotes/stocks/russia/?pageNumber=10'
]

class MoexParser:

    def __init__(self):

        self.names = []
        self.last_price = []
        self.per_change_price = []
        self.opening = []
        self.max_price = []
        self.min_price = []
        self.closing = []
        self.amount = []
        self.update_time = []
        self.info = dict()
        self.all_info = dict()

    # Info from page
    def get_info(self, url=DEFAULT_URL_ARR[0]):

        page = requests.get(url)
        soup = BeautifulSoup(page.text, "html.parser")
        table = soup.findAll('table', class_='QuoteTable__table--RPe')
        soup = BeautifulSoup(str(table), "html.parser")
        tr_arr = soup.findAll('tr')

        soup = BeautifulSoup(str(tr_arr), "html.parser")
        tr_arr = soup.findAll('tr')

        for tr in tr_arr:

            soup = BeautifulSoup(str(tr), "html.parser")
            name = soup.find('a', class_='InstrumentLink__instrument--1PO')

            if name is None:
                continue

            if name is not None:
                self.names.append(name.text)

            arr_td = soup.findAll('td', class_='QuoteTable__tableCell--1Lh QuoteTable__right--166')

            count = 0

            for i in arr_td:
                soup = BeautifulSoup(str(i), "html.parser")

                if count == 0:
                    self.last_price.append(soup.find('span').text)

                if count == 1:
                    soup = BeautifulSoup(str(soup.find('span')), "html.parser")
                    self.per_change_price.append(soup.find('span').text)
                    soup = BeautifulSoup(str(i), "html.parser")

                if count == 2:
                    self.opening.append(soup.find('span').text)

                if count == 3:
                    self.max_price.append(soup.find('span').text)

                if count == 4:
                    self.min_price.append(soup.find('span').text)

                if count == 5:
                    self.closing.append(soup.find('span').text)

                if count == 6:
                    self.amount.append(soup.find('span').text)

                if count == 7:
                    self.update_time.append(soup.find('span').text)

                count += 1

        for i in range(len(self.names)):
            tmp = []
            tmp.append(self.last_price[i])
            tmp.append(self.per_change_price[i])
            tmp.append(self.opening[i])
            tmp.append(self.max_price[i])
            tmp.append(self.min_price[i])
            tmp.append(self.closing[i])
            tmp.append(self.amount[i])
            tmp.append(self.update_time[i])

            self.info[self.names[i]] = tmp

        return self.info

    # Info from all pages
    def get_all_pages_info(self, url_arr=DEFAULT_URL_ARR):

        for url in url_arr:
            info = self.get_info(url)
            for i in info.keys():
                self.all_info[i] = info[i]

        return self.all_info

    def show_info(self):

        print('%15s' % 'Инструмент', end=" ")
        print('%15s' % 'Посл. сделка', end=" ")
        print('%15s' % 'Изменение', end=" ")
        print('%15s' % 'Открытие', end=" ")
        print('%15s' % 'Макс. цена', end=" ")
        print('%15s' % 'Мин. цена', end=" ")
        print('%15s' % 'Закрытие', end=" ")
        print('%15s' % 'Оборот', end=" ")
        print('%15s' % 'Время обновл.')

        for i in self.all_info.keys():
            print('%15s' % str(i), end=" ")
            for j in self.all_info[i]:
                print('%15s' % str(j), end=" ")
            print()