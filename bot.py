import config
import telebot
import sqlite3
import json
from datetime import date
from datetime import datetime
from telebot import types
from calcPFC import Bujda

currentFoodData = {
    'Name': '',
    'Prot': '',
    'Fat': '',
    'Carb': '',
    'KCal': '',
    'Weight': ''
}
bujda = Bujda()
con = sqlite3.connect('/home/pi/FoodProcessor/ProtFatCarbKCal.db',
                      check_same_thread=False)
cur = con.cursor()
conMenu = sqlite3.connect('/home/pi/FoodProcessor/menu.db',
                      check_same_thread=False)
curMenu = conMenu.cursor()

bot = telebot.TeleBot(config.token)


def get_today_stats():
    print(f"SELECT * FROM PFCKC date = '{str(date.today())}'")
    dt = cur.execute(
        f"SELECT * FROM PFCKC WHERE date = ?",
        (str(date.today()), ),
    ).fetchall()

    return dt


def parse_msg(msg):
    msg = '{"Name":"",' + msg + '}'
    msg = msg.replace(' ', ',')
    msg = msg.replace('Б', '"Prot"')
    msg = msg.replace('Ж', '"Fat"')
    msg = msg.replace('У', '"Carb"')
    msg = msg.replace('К', '"KCal"')
    msg = msg.replace('В', '"Weight"')
    msg = msg.replace(':', " : ")
    msg = json.loads(msg)
    return msg


def storeData(data: dict):
    for key in data.keys():
        temp = data.get(key)
        if temp != '':
            currentFoodData[key] = temp


def saveData(data):
    cur.execute("INSERT INTO PFCKC VALUES (?,?,?,?,?,?,?)", (
        date.today(),
        datetime.now().strftime("%H:%M:%S"),
        data.get('Name', ''),
        data.get('Prot'),
        data.get('Fat'),
        data.get('Carb'),
        data.get('KCal'),
    ))
    con.commit()
    global currentFoodData
    currentFoodData = {
        'Name': '',
        'Prot': '',
        'Fat': '',
        'Carb': '',
        'KCal': '',
        'Weight': ''
    }


def calcData(data: dict):
    data['Prot'] = data['Prot'] * data['Weight'] / 100.0
    data['Fat'] = data['Fat'] * data['Weight'] / 100.0
    data['Carb'] = data['Carb'] * data['Weight'] / 100.0
    data['KCal'] = data['KCal'] * data['Weight'] / 100.0
    return data


def checkFoodData():
    notEnoughData = []
    for key in currentFoodData.keys():
        temp = currentFoodData.get(key)
        if temp == '':
            notEnoughData.append(key)

    return notEnoughData


@bot.message_handler(commands=['info'])
def info_responce(message):
    bot.send_message(message.chat.id, '/info')
    bot.send_message(message.chat.id, '/status')
    bot.send_message(message.chat.id, '/add')
    bot.send_message(message.chat.id, '/process')
    bot.send_message(message.chat.id, '/clear')
    bot.send_message(message.chat.id, '/food_list')
    #bot.send_message(message.chat.id, '/calc_PFC')


@bot.message_handler(commands=['status'])
def status_responce(message):
    DayFoodData = {'Prot': 0, 'Fat': 0, 'Carb': 0, 'KCal': 0}
    #print(get_today_stats())
    for row in get_today_stats():
        if row[3]:
            DayFoodData['Prot'] += row[3]
        if row[4]:
            DayFoodData['Fat'] += row[4]
        if row[5]:
            DayFoodData['Carb'] += row[5]
        if row[6]:
            DayFoodData['KCal'] += row[6]
    for key in DayFoodData:
        try:
            DayFoodData[key] = round(DayFoodData[key])
        except:
            pass
    bot.send_message(
        message.chat.id,
        f'Норма:\nProt:140, Fat:70, Carb:210, KCal:{140*4 + 70*9 + 210*4}')
    bot.send_message(message.chat.id, f'Сегодня нажрал:\n{DayFoodData}')
    bot.send_message(
        message.chat.id,
        f"Осталось:\nProt:{140-DayFoodData.get('Prot')}, Fat:{70-DayFoodData.get('Fat')}, Carb:{210-DayFoodData.get('Carb')}, KCal:{140*4 + 70*9 + 210*4 -DayFoodData.get('KCal')}"
    )


@bot.message_handler(commands=['add'])
def add_responce(message):
    try:
        component = parse_msg(message.text)
        data = {k: component.get(k) for k in ['Prot', 'Fat', 'Carb', 'Weight']}
        bujda.addComponent(data)
        bot.send_message(message.chat.id, 'K, chum!')
    except:
        bot.send_message(message.chat.id, 'WTF, Nigga!')


@bot.message_handler(commands=['process'])
def process_responce(message):
    bot.send_message(message.chat.id,bujda.calculate(message.text))


@bot.message_handler(commands=['food_list'])
def food_list_responce(message):
    pass


@bot.message_handler(commands=['calc_PFC'])
def calc_PFC_responce(message):
    pass


@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):  # Название функции не играет никакой роли

    data = message.text
    data = data.replace(' ', ',')
    data = data.replace(',,', ',')
    data = data.replace(':,', ':')
    #data = data.split(',')
    try:
        data = parse_msg(data)
    except:
        bot.send_message(message.chat.id,
                         'ERROR!\nExpected format X:nnn Y:mmm Z:kkk')
        return

    # match len(data.split(',')):
    #     case 6:
    #         # Апельсин,Б:123,Ж:123,У:123,К:123,В:123
    #         if ['Б:','Ж:','У:','К:','В:'] in data:
    #             data = parse_msg(data)
    #             data = calcData(data)
    #
    #             pass
    #         else:
    #             print('wtf')
    #     case 5:
    #         # Апельсин,Б:123,Ж:123,У:123,В:123 # Апельсин,Б:123,Ж:123,У:123,К:123 # Б:123,Ж:123,У:123,К:123,В:123
    #         if ['Б:','Ж:','У:','К:'] in data:
    #             data = parse_msg(data)
    #             pass
    #         else:
    #             print('wtf')
    #         print('good')
    #     case 4:
    #         # Апельсин,Б:123,Ж:123,У:123 # Б:123,Ж:123,У:123,В:123 # Б:123,Ж:123,У:123,К:123
    #         data = parse_msg(data)
    #         storeData(data)
    #     case 3:
    #         # Б:123,Ж:123,У:123
    #         data = parse_msg(data)
    #     case 1:
    #         # Апельсин # 123 # Б:123 # Ж:123 # У:123 # К:123 # В:123
    #         data = parse_msg(data)

    storeData(data)
    emptyData = checkFoodData()
    if ['KCal'] in emptyData:
        currentFoodData[
            'KCal'] = currentFoodData['Prot'] * 4 + currentFoodData[
                'Fat'] * 9 + currentFoodData['Carb'] * 4
        emptyData = checkFoodData()

    if emptyData and (emptyData != ['Name']):
        #print(emptyData)
        for empty in emptyData:
            bot.send_message(message.chat.id, 'Please enter ' + empty)
    else:
        FoodData = calcData(currentFoodData)
        saveData(FoodData)
        status_responce(message)
        #DayFoodData = {'Prot': 0, 'Fat': 0, 'Carb': 0, 'KCal': 0}
        ##print(get_today_stats())
        #for row in get_today_stats():
        #    if row[3]:
        #        DayFoodData['Prot'] += row[3]
        #    if row[4]:
        #        DayFoodData['Fat'] += row[4]
        #    if row[5]:
        #        DayFoodData['Carb'] += row[5]
        #    if row[6]:
        #        DayFoodData['KCal'] += row[6]
        #for key in DayFoodData:
        #    try:
        #        DayFoodData[key] = round(DayFoodData[key])
        #    except:
        #        pass
        #bot.send_message(message.chat.id, f'сегодня нажрал: {DayFoodData}')


if __name__ == '__main__':
    bot.infinity_polling()
