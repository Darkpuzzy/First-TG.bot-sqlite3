import datetime
import sqlite3
import time

URL_DB = 'Db/DatebaseTest2.db' # const


def init_database():
    with sqlite3.connect(URL_DB) as db:
        cursor = db.cursor()
        cursor.execute(""" CREATE TABLE IF NOT EXISTS Betlog(
        Message_id INTEGER PRIMARY KEY ,
        User_id INTEGER NOT NULL,
        Bet INTEGER NOT NULL,
        Opperand TEXT,
        Date DATATIME NOT NULL
        )""" )
        db.commit()

# Добавление в базу данных


def intbase(message_id,user_id,user_bet,user_opp,user_date):
    empy_parameters = (message_id,user_id, user_bet, user_opp, user_date)
    with sqlite3.connect(URL_DB) as db:
        cursor = db.cursor()
        cursor.execute(""" INSERT INTO Betlog(Message_id,User_id, Bet, Opperand, Date) VALUES(?,?,?,?,?); """, empy_parameters)
        db.commit()
# Формирование запросов


def select_m(user_id, user_date):
    with sqlite3.connect(URL_DB) as db:
        cursor = db.cursor()
        #user_date1 = '2021.09.01'
        #user_date2 = '2021.09.27'
        cursor.execute(f""" SELECT * FROM Betlog WHERE User_id = {user_id} AND Date BETWEEN '{user_date}.01' AND '{user_date}.31' """)
        result = cursor.fetchall()
    return result


def select_db(user_id, user_date):
    if user_date != None:
        with sqlite3.connect(URL_DB) as db:
            cursor = db.cursor()
            cursor.execute(f""" SELECT * FROM Betlog WHERE User_id = {user_id} AND Date = '{user_date}' """)
            result = cursor.fetchall()
        return result
    else:
        with sqlite3.connect(URL_DB) as db:
            cursor = db.cursor()
            cursor.execute(f""" SELECT * FROM Betlog WHERE User_id = {user_id} """)
            result1 = cursor.fetchall()
        return result1

    
def edit_message(user_id, message_id):
    with sqlite3.connect(URL_DB) as db:
        cursor = db.cursor()
        cursor.execute(f"""DELETE FROM Betlog WHERE User_id = {user_id} AND Message_id = {message_id}""")
        db.commit()


if __name__ == '__main__':
    init_database() # Иницилизация ( миграция ) таблиц БД
    dict_db = {'message_id': 2225, 'user_id': 411067032, 'text': 19, 'opperand': '-', 'date': 1629380182}

    use_date = dict_db['date']
    named_tuple = time.localtime(use_date)  # получить struct_time
    time_string = time.strftime("%Y.%m.%d", named_tuple)

    message_id = dict_db['message_id']
    user_id = dict_db['user_id']
    user_bet = dict_db['text']
    user_opp = dict_db['opperand']
    user_date = time_string
    empy_parameters = (message_id, user_id, user_bet, user_opp, user_date)

    edit_message(user_id,message_id)
    #intbase(message_id, user_id, user_bet, user_opp, user_date)
