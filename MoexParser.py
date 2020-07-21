import aiomoex
import asyncio

import MoexDataWorker

'''

    2 БД:
        1) Одна таблица - SEC_ID и SHORTNAME.
        2) Много таблиц с названиями от SEC_ID по две колонки: дата и цена закрытия.

'''

class MoexParser:

    def __init__(self):
        request_url = ('https://iss.moex.com/iss/engines/stock/'
                   'markets/shares/boards/TQBR/securities.json')
        self.iss = aiomoex.ISSClient(request_url)
        self.iss.start_session()

    # date format - 'yyyy-mm-dd' -> string
    async def get_stock_hystoryinfo(self, sec_id, from_date=None, till_date=None):

        info = dict()
        info_block = []

        all_info = await aiomoex.get_market_history(sec_id)

        if from_date == None and till_date == None:

            for i in all_info:
                info_block.append(i)

            info[sec_id] = info_block

        elif not from_date == None and not till_date == None:

            # 2011-11-21 yyyy-mm-dd
            _from_date = [int(i) for i in from_date.split('-')]
            _till_date = [int(i) for i in till_date.split('-')]

            for i in all_info:
                date = self.make_arr_from_date(str(i['TRADEDATE']))

                if _from_date[0] <= date[0] <= _till_date[0] and \
                        _from_date[1] <= date[1] <= _till_date[1] and \
                        _from_date[2] <= date[2] <= _till_date[2]:

                    info_block.append(i)

        elif from_date == None and not till_date == None:

            # 2011-11-21 yyyy-mm-dd
            _till_date = [int(i) for i in till_date.split('-')]

            for i in all_info:
                date = self.make_arr_from_date(str(i['TRADEDATE']))

                if date[0] <= _till_date[0] and \
                        date[1] <= _till_date[1] and \
                        date[2] <= _till_date[2]:
                    info_block.append(i)

        elif not from_date == None and till_date == None:

            # 2011-11-21 yyyy-mm-dd
            _from_date = [int(i) for i in from_date.split('-')]

            for i in all_info:
                date = self.make_arr_from_date(str(i['TRADEDATE']))

                if date[0] >= _from_date[0] and \
                        date[1] >= _from_date[1] and \
                        date[2] >= _from_date[2]:
                    info_block.append(i)

            info[sec_id] = info_block

        return info

    # Сохраняет в одноименную таблицу бд(дата, цена закрытия) информацию об акции
    async def save_stock_hystoryinfo(self, sec_id, from_date=None, till_date=None):

        # Получение полной информации об акции
        info = (await self.get_stock_hystoryinfo(sec_id, from_date, till_date))[str(sec_id)]

        # Объект для работы с бд
        mdw = MoexDataWorker.MoexDataWorker()

        for d in info:
            tmp = []

            # Получение даты закрытия и цены
            tmp.append(d['TRADEDATE'])
            tmp.append(d['CLOSE'])

            mdw.add_history_stock_data(sec_id, tmp)

    # Сохраняет в бд(дата, цена закрытия) информацию обо всех доступных акциях на рынке
    async def save_all_stocks_hystoryinfo(self, start=0):
        # Получение всех кодовых названий акций на бирже
        secid_arr = (await self.get_all_stocks_secid_and_shortnames()).keys()
        secid_count = len(secid_arr)

        secid_arr = list(secid_arr)[start:]

        count = start + 1
        # Сохранение каждой акции
        for sec_id in secid_arr:
            print(str(sec_id) + ' - ' + str(count) + '/' + str(secid_count) + ' : ' + str((count/secid_count) * 100) + '%')
            await self.save_stock_hystoryinfo(sec_id)
            count += 1

    # Сохранение в бд(кодовое название, полное название) информации обо всех акций
    # По идее запускается один раз
    async def save_all_stocks_secid_shortnames(self):
        data = await self.get_all_stocks_secid_and_shortnames()

        mdw = MoexDataWorker.MoexDataWorker()

        for sec_id in data.keys():
            print(sec_id, data[sec_id])
            mdw.add_secid_and_shortname(sec_id, data[sec_id])

    async def get_all_stocks_secid_and_shortnames(self):
        data = await aiomoex.get_board_securities()
        info = dict()

        for i in data:
            info[i['SECID']] = i['SHORTNAME']

        return info

    async def get_last_info_about_stocks(self, sec_id=[]):

        if len(sec_id) == 0:
            return dict()

        secid_arr = sec_id

        data = dict()

        for i in secid_arr:
            stock_info = await self.get_stock_hystoryinfo(i)
            stock_info = stock_info[i]
            stock_info = stock_info[len(stock_info) - 1]

            tmp = []

            ''' !!! MUST CORRECT !!! '''
            tmp.append(i)  # SHORTNAME
            tmp.append(stock_info['TRADEDATE'])  # last update_time
            tmp.append(stock_info['CLOSE'])  # close price

            data[i] = tmp

        return data

    async def get_last_info_about_all_stocks(self):
        secid_shortnames = await self.get_all_stocks_secid_and_shortnames()

        data = dict()

        for sec_id in secid_shortnames.keys():
            stock_info = await self.get_stock_hystoryinfo(sec_id)
            stock_info = stock_info[sec_id]
            stock_info = stock_info[len(stock_info) - 1]

            tmp = []

            tmp.append(secid_shortnames[sec_id]) # SHORTNAME
            tmp.append(stock_info['TRADEDATE']) # last update_time
            tmp.append(stock_info['CLOSE']) # close price

            data[sec_id] = tmp

        return data

    async def save_last_info_about_all_stocks(self):
        secid_shortnames = await self.get_all_stocks_secid_and_shortnames()

        data = dict()

        mdw = MoexDataWorker.MoexDataWorker()

        for sec_id in secid_shortnames.keys():
            stock_info = await self.get_stock_hystoryinfo(sec_id)
            stock_info = stock_info[sec_id]
            stock_info = stock_info[len(stock_info) - 1]

            tmp = []

            tmp.append(secid_shortnames[sec_id]) # SHORTNAME
            tmp.append(stock_info['TRADEDATE']) # last update_time
            tmp.append(stock_info['CLOSE']) # close price

            mdw.add_secid_and_shortname(sec_id, tmp[0])
            mdw.add_history_stock_data(sec_id, [tmp[1], tmp[2]])

    async def close(self):
        await self.iss.close_session()

    def make_arr_from_date(self, str_date):
        return [int(i) for i in str_date.split('-')]
