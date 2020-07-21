import sqlite3

class DataWorker:

    def __init__(self):

        self.DATABASE_NAME = "stocksdata.db"

    def create_table(self, name):
        conn = sqlite3.connect(self.DATABASE_NAME)
        cursor = conn.cursor()

        sql = "CREATE TABLE %s\
                                      (last_price text, per_change_price text, opening text,\
                                       max_price text, min_price text, closing text, \
                                       amount text, update_time text)\
                                   " % str("'" + str(name) + "'")

        cursor.execute(sql)

    def create_database(self, stocks_names):
        conn = sqlite3.connect(self.DATABASE_NAME)

        for name in stocks_names:
            self.create_table(name)

    def update_data(self, all_info):
        conn = sqlite3.connect(self.DATABASE_NAME)
        cursor = conn.cursor()

        stock_names_in_database = self.get_stocknames_from_db()

        for name in all_info.keys():

            if not name in stock_names_in_database:
                self.create_table(name)

            last_update_time = str(self.get_last_update_time(name, cursor))

            # Если дата обновления изменилась, то добавляем данные в таблицу
            if last_update_time[1:len(last_update_time)-1] != all_info[name][7]:

                data = []

                tmp = 0
                for i in all_info[name]:
                    if tmp == 0:
                        data.append("'" + str(i)[:len(str(i))-2] + "'")
                    elif tmp == 1:
                        data.append("'" + str(i)[:len(str(i))-1] + "'")
                    else:
                        data.append("'" + str(i) + "'")
                    tmp += 1

                cursor.execute("INSERT INTO '" + str(name) + "' VALUES (?,?,?,?,?,?,?,?) ", data)
                conn.commit()


    def get_last_update_time(self, stock_name, cursor):
        #conn = sqlite3.connect(self.DATABASE_NAME)
        #cursor = conn.cursor()

        cursor.execute("SELECT update_time FROM '" + str(stock_name) + "'")
        update_time_arr = cursor.fetchall()

        if len(update_time_arr) == 0 or update_time_arr == None:
            return None

        return update_time_arr[len(update_time_arr) - 1][0]

    def get_stock_info(self, stock_name):
        conn = sqlite3.connect(self.DATABASE_NAME)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM '" + str(stock_name) + "'")

        return cursor.fetchall()

    def get_stocknames_from_db(self):
        conn = sqlite3.connect(self.DATABASE_NAME)
        cursor = conn.cursor()

        cursor.execute("SELECT name from sqlite_master where type='table'")

        ans = cursor.fetchall()
        stocknames = []

        for i in ans:
            stocknames.append(i[0])

        return stocknames

    def get_info_about_all_stocks(self):
        stocknames = self.get_stocknames_from_db()
        all_info = dict()

        for i in stocknames:
            all_info[i] = self.get_stock_info(i)

        return all_info
