#import MoexParser
import sqlite3

'''

    2 БД:
        1) Одна таблица - SEC_ID и SHORTNAME.
        2) Много таблиц с названиями от SEC_ID по две колонки: дата и цена закрытия.

'''

class MoexDataWorker():

    def __init__(self):

        self.SECID_SHORTNAME_DATABASE_NAME = 'secid_shortname_data.db'
        self.SECID_SHORTNAME_TABLENAME = 'std_table'
        self.HISTORY_STOCKS_DATABASE_NAME = 'history_stocks_data.db'

    def create_table_ssdb(self):
        conn = sqlite3.connect(self.SECID_SHORTNAME_DATABASE_NAME)
        cursor = conn.cursor()

        sql = "CREATE TABLE %s\
                                      (secid text, shortname text)\
                                   " % str("'" + str(self.SECID_SHORTNAME_TABLENAME) + "'")

        cursor.execute(sql)

    def create_table_hsdb(self, sec_id):
        conn = sqlite3.connect(self.HISTORY_STOCKS_DATABASE_NAME)
        cursor = conn.cursor()

        sql = "CREATE TABLE %s\
                                      (date text, close_price text)\
                                   " % str("'" + str(sec_id) + "'")

        cursor.execute(sql)

    def get_last_date(self, sec_id, cursor):

        try:
            cursor.execute("SELECT date FROM '" + str(sec_id) + "'")
            date_arr = cursor.fetchall()
            return date_arr[len(date_arr) - 1][0]

        except Exception as e:
            return None

    def get_stock_info(self, sec_id):
        conn = sqlite3.connect(self.SECID_SHORTNAME_DATABASE_NAME)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM '" + str(self.SECID_SHORTNAME_TABLENAME) + "' WHERE secid LIKE '" + str(sec_id) + "'")

        ans = []

        ans.append(cursor.fetchall()[0])
        #ans.append(cursor.fetchall()[1])

        conn = sqlite3.connect(self.HISTORY_STOCKS_DATABASE_NAME)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM '" + str(sec_id) + "'")

        ans += cursor.fetchall()

        return ans

    def add_secid_and_shortname(self, sec_id, shortname, conn=None):
        if conn == None:
            conn = sqlite3.connect(self.SECID_SHORTNAME_DATABASE_NAME)

        cursor = conn.cursor()

        #cursor.execute("SELECT * FROM '" + self.SECID_SHORTNAME_TABLENAME + "' WHERE secid LIKE " + str(sec_id))
        #tmp = cursor.fetchall()
        tmp = None

        if tmp == None or len(tmp) == 0:
            cursor.execute("INSERT INTO '" + self.SECID_SHORTNAME_TABLENAME + "' VALUES (?,?) ", [sec_id, shortname])
            conn.commit()



    def add_history_stock_data(self, sec_id, data, conn=None):
        if conn == None:
            conn = sqlite3.connect(self.HISTORY_STOCKS_DATABASE_NAME)
        cursor = conn.cursor()

        last_date = self.make_arr_from_date(self.get_last_date(sec_id, cursor))
        new_date = self.make_arr_from_date(data[0])

        if not (last_date == None) and not (new_date == None):
            if last_date[0] > new_date[0] or (last_date[0] == new_date[0] and last_date[1] >= new_date[1]) or \
                    (last_date[0] == new_date[0] and last_date[1] == new_date[1] and last_date[2] >= new_date[2]):
                return

        try:
            cursor.execute("INSERT INTO '" + str(sec_id) + "' VALUES (?,?) ", [data[0], data[1]])
            conn.commit()
        except sqlite3.OperationalError as e:
            self.create_table_hsdb(sec_id)
            self.add_history_stock_data(sec_id, data, conn)

    def get_all_secid(self):
        conn = sqlite3.connect(self.SECID_SHORTNAME_DATABASE_NAME)
        cursor = conn.cursor()

        cursor.execute("SELECT secid FROM '" + str(self.SECID_SHORTNAME_TABLENAME) + "'")

        return cursor.fetchall()

    def make_arr_from_date(self, str_date):
        if str_date == None:
            return None
        return [int(i) for i in str_date.split('-')]