import requests
import json
import copy
import datetime
import time
from time import sleep, strftime
import par as db

now = datetime.datetime.now()
now_str = now.strftime('%Y.%m.%d') # Для улучшения поиска данных лучше убрать часы а оставить только сутки.

token_bot = ""
URL_bot = "https://api.telegram.org/bot" + token_bot + '/'


def get_updates():
    url = URL_bot + 'getUpdates'
    req = requests.get(url)
    return req.json()

global last_update_id
last_update_id = 0


def get_message():
    global last_update_id
    data = get_updates()
    ash = last_object = data['result']
    if ash == []:
        while ash == []:
            sleep(6)
            data_up = get_updates()
            if data_up['result'] != []:
                break
    else:
        last_object = data['result'][-1]
        now_update_id = last_object['update_id']

        if last_update_id != now_update_id:
            last_update_id = now_update_id

            b = 'edited_message' in data['result'][-1]

            if b == True:
                recursion_edit = recursion(data=data)
                if 'edited_message' in recursion(data=data):
                    not_found_message_id = recursion_edit['edited_message']['message_id']
                    not_found_user_id = recursion_edit['edited_message']['chat']['id']
                    db.edit_message(user_id=not_found_user_id, message_id=not_found_message_id)
                    return editor_message(data=data)
                else:
                    recursion_edit_mess_id = recursion_edit['message']['message_id']
                    recursion_edit_user_id = recursion_edit['message']['chat']['id']
                    db.edit_message(user_id=recursion_edit_user_id, message_id=recursion_edit_mess_id)
                    return editor_message(data=data)
            else:
                message_id = data['result'][-1]['message']['message_id']
                date = data['result'][-1]['message']['date']
                user_id = data['result'][-1]['message']['chat']['id']
                message_text = data['result'][-1]['message']['text']
                message = {'message_id':message_id, 'user_id': user_id, 'text': message_text, 'date': date}
                return message
        url = URL_bot + f'getUpdates?offset={now_update_id - 20}'  # чистка очереди запросов,что бы обойти лимит
        requests.get(url)
    return None


def editor_message(data: dict):
    message_id = data['result'][-1]['edited_message']['message_id']
    date_ed = data['result'][-1]['edited_message']['edit_date']
    user_ids = data['result'][-1]['edited_message']['chat']['id']
    message_text_ed = data['result'][-1]['edited_message']['text']
    message_ed = {'message_id': message_id, 'user_id': user_ids,
                  'text': message_text_ed, 'date': date_ed}
    return message_ed


def recursion(data: dict):
    message_id = data['result'][-1]['edited_message']['message_id']
    cheak_data = []
    edit_mes = data['result']
    cheak_data.extend(edit_mes)
    flag = True
    while flag:
        find_id = cheak_data.pop(-1)
        try:
            respond = cheak_data[-1]
            if 'message' not in respond:
                key = respond['edited_message']
            else:
                key = respond['message']
            vallues = key.items()
            alpha = ('message_id', message_id) in vallues
            if alpha == True:
                flag = False
                return respond
        except IndexError:
            return data['result'][-1]
    if cheak_data:
        return recursion(cheak_data)

    
def send_message(user_id, text):
    url = f"{URL_bot}sendmessage?chat_id={user_id}&text={text}"
    requests.get(url)

    
def valid_bet(answer: dict):
    bet = answer['text']
    # Пишем для операнда "-" "+". isdigit() - проверяет все ли числа в строчке
    if bet[0] == "-":
        if bet[1:].isdigit():
            answer['operand'] = '-'
            answer['text'] = int(bet[1:])
            return answer

    elif bet[0] == "+":
        if bet[1:].isdigit():
            answer['operand'] = '+'
            answer['text'] = int(bet[1:])
            return answer

    elif bet.isdigit():
        if bet[0:].isdigit():
            answer['operand'] = '+'
            answer['text'] = int(bet[0:])
            return answer

        
def select_sum(call):
    select_sum = 0
    for table in call:
        if table[3] == '+':
            select_sum += table[2]
        if table[3] == '-':
            select_sum -= table[2]
    return select_sum


def valid_cheaker(cheak_text,u_i):
    user_id = u_i
    b = cheak_text
    date_to_split = b.split('.',3)
    if len(date_to_split) == 3 or len(date_to_split) == 2:
        date_to_join = ''.join(date_to_split)
        try:
            date_us_int = int(date_to_join)
            return cheak_text
        except ValueError:
            print('Not a numbers')
            return send_message(user_id,'Введите дату корректно!')
    else:
        return send_message(user_id, 'Введеная вами дата некорректна.')


def main():

    db_bet = []
    dict_users = {}

    while True :
        answer = get_message()
        if answer != None:
            user_id = answer['user_id']
            text = answer['text']
            bet_dict = answer.copy()
            valid_dict = valid_bet(bet_dict)
           
            if valid_dict != None:
                us_date = valid_dict['date']
                named_tuple = time.localtime(us_date)  # получить struct_time
                time_string = strftime("%Y.%m.%d", named_tuple)
                mess_id = valid_dict['message_id']
                use_id = valid_dict['user_id']
                use_bet = valid_dict['text']
                use_opp = valid_dict['operand']
                use_date = time_string
                db.intbase(message_id=mess_id,user_id=use_id,user_bet=use_bet,user_opp=use_opp,user_date=use_date)

            if "/start" in text:
                send_message(user_id,'Добро пожаловать, для начала работы впишите /work')

            if "/work" in text:
                send_message(user_id, 'Бот начал считывать информацию.Для просмотра результата введите /total, /reset - что бы обнулить')

            if '/total' in text:
                send_message(user_id, f'Чтобы узнать статистику за {now_str} введите /daytotal. Больше команд в /helpt')
                print(get_message())

            if '/helpt' in text:
                send_message(user_id, '/daytotal - узнать статистику за текущий день.\n /dtotal - статистика за определенный день.\n /mtotal - статистика за определенный месяц.\n /alltotal - статистика за все время.')

            if '/daytotal' in text:
                send_message(user_id, f'Статистика за {now_str} .')
                us_id = answer['user_id']
                date_bet = answer['text']
                d_t = db.select_db(user_id=us_id,user_date=now_str)
                print(d_t)
                dayt = select_sum(d_t)
                print(f"TEXT FOR DB ----> {date_bet}")
                send_message(user_id, f'Ваш результат: {dayt}')

            if '/dtotal' in text:
                send_message(user_id,'Введите дату за которую хотите узнать статистику в формате: | year.mouth.day | 2021.08.20 |\nЧто бы сменить функцию впишите "/stop" ')
                flag = True
                while flag:
                    sleep(5)
                    bad_text = get_message()

                    if bad_text == None:
                        send_message(user_id,'Ожидаю вашей команды...')
                        sleep(3)
                    else:
                        b_txt = bad_text['text']
                        if b_txt == '/stop':
                            send_message(user_id, 'Сброс функции успешен!')
                            flag = False
                            break
                        else:
                            valid = valid_cheaker(cheak_text=b_txt, u_i=user_id)
                            if valid != b_txt:
                                print(valid)
                                sleep(3)
                            else:
                                d_total = db.select_db(user_id=user_id,user_date=b_txt)
                                dtotal = select_sum(d_total)
                                if d_total == []:
                                    send_message(user_id,'Отсутствуют данные за эту дату.Введите снова /dtotal и нужную дату')
                                else:
                                    send_message(user_id, f'Статистика за {valid}: {dtotal}')
                                flag = False
                                break

            if '/alltotal' in text:
                send_message(user_id, 'Статистика за все ваше время ставок')
                a_t = db.select_db(user_id=user_id,user_date=None) 
                all_total = select_sum(a_t)
                send_message(user_id, f'Ваш результат:{all_total}')

            if '/mtotal' in text:
                flag_m = True
                msum = 0
                send_message(user_id, 'Введите месяц за который хотите узнать статистику.\n Указывать месяцы 1-12 и так же год.\n Формат записи | YEARS.MOUTH | 2022.09 |\n /stop - для завершения функции ')
                while flag_m:
                    sleep(5)
                    n_message = get_message() # Вызов обновления сообщения
                    if n_message == None:
                        send_message(user_id, 'Ожидаю вашей команды...')
                        sleep(4)
                    else:
                        b_txt1 = n_message['text']
                        if b_txt1 == '/stop':
                            send_message(user_id, 'Сброс функции успешен!')
                            flag = False
                        else:
                            valid1 = valid_cheaker(cheak_text=b_txt1, u_i=user_id)
                            if valid1 != b_txt1:
                                print(valid1)
                                sleep(3)
                            else:
                                print(f'B TXT1 ===== {b_txt1}')
                                m_total = db.select_m(user_id=user_id, user_date=b_txt1)
                                mtotal = select_sum(m_total)
                                if m_total == []:
                                    send_message(user_id, 'Отсутствуют данные за месяц.')
                                else:
                                    send_message(user_id, f'Ваш результат: {mtotal}')
                                flag = False


            if "/reset" in text:
                db_bet.clear()
                dict_users.clear()
                send_message(user_id,'Обнуление произведено успешно!')
        sleep(1)

        
if __name__ == '__main__':
    main()
    
    
#dit = get_updates()
    #print(type(dit))
    #with open('newbot.json', 'w') as file:
       # json.dump(dit, file, indent=2, ensure_ascii=False)
