import config
import telebot
import sqlite3
import json
from datetime import date
from datetime import datetime
from telebot import types
from calcPFC import Bujda

cur_weight = 100
fat_percent = 25
lean_mass = cur_weight*(1-fat_percent/100)
norm = {
    'Prot':lean_mass*2.2,
    'Fat':lean_mass*0.75,
    'Carbs':lean_mass*3,
    'KCal':0,
    
}
norm['KCal'] = norm['Carbs'] * 4 + norm['Fat'] * 9 + norm['Prot']*4

currentFoodData = {
    'Name': '',
    'Prot': '',
    'Fat': '',
    'Carb': '',
    'KCal': '',
    'Weight': ''
}
targets = [' ','prot','fat','carb','kcal','weight','б','ж','у','к','в',':']
new_texts = [',','"Prot"','"Fat"','"Carb"','"KCal"','"Weight"','"Prot"','"Fat"','"Carb"','"KCal"','"Weight"'," : "]
bujda = Bujda()
con = sqlite3.connect('/var/services/homes/manornot/bots/FoodProcessor/ProtFatCarbKCal.db',
                      check_same_thread=False)
cur = con.cursor()
conMenu = sqlite3.connect('/var/services/homes/manornot/bots/FoodProcessor/menu.db',
                      check_same_thread=False)
curMenu = conMenu.cursor()

bot = telebot.TeleBot(config.token)


def get_today_stats():
    #print(f"SELECT * FROM PFCKC date = '{str(date.today())}'")
    dt = cur.execute(
        f"SELECT * FROM PFCKC WHERE date = ?",
        (str(date.today()), ),
    ).fetchall()

    return dt


def parse_msg(msg):
    msg = msg.lower()
    msg = '{"Name":"",' + msg + '}'
    [msg:=msg.replace(trgt,new_txt) for trgt,new_txt in zip(targets,new_texts)]
    #msg = msg.replace(' ', ',')
    #msg = msg.replace('Б', '"Prot"')
    #msg = msg.replace('Ж', '"Fat"')
    #msg = msg.replace('У', '"Carb"')
    #msg = msg.replace('К', '"KCal"')
    #msg = msg.replace('В', '"Weight"')
    #msg = msg.replace(':', " : ")

    msg = json.loads(msg)
    ##print(msg)
    return msg


def storeData(data: dict):
    #print(f'store data - {data}')
    for key in data.keys():
        temp = data.get(key)

        if temp != '':
            currentFoodData[key] = temp
            #print(key,currentFoodData[key])


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
        #print(currentFoodData)
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
    ##print(get_today_stats())
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
        f'Норма:\nProt:{norm["Prot"]}, Fat:{norm["Fat"]}, Carb:{norm["Carbs"]}, KCal:{norm["KCal"]}')
    bot.send_message(message.chat.id, f'Сегодня нажрал:\n{DayFoodData}')
    bot.send_message(
        message.chat.id,
        f"Осталось:\nProt:{norm['Prot']-DayFoodData.get('Prot')}, Fat:{norm['Fat']-DayFoodData.get('Fat')}, Carb:{norm['Carbs']-DayFoodData.get('Carb')}, KCal:{norm['KCal'] -DayFoodData.get('KCal')}"
    )

@bot.message_handler(commands=['clear'])
def clear_responce(message):
    bujda.clear()
    bot.send_message(message.chat.id, 'Sector clear!')

@bot.message_handler(commands=['add'])
def add_responce(message):
    try:
        component = parse_msg(message.text.replace('/add ',''))
        data = {k: component.get(k,0) for k in ['Prot', 'Fat', 'Carb', 'Weight']}
        if data['Weight'] == 0:
            bot.send_message(message.chat.id, 'Some thin air!')
            return
        bujda.addComponent(data)
        bot.send_message(message.chat.id, 'K, chum!')
    except:
        bot.send_message(message.chat.id, 'WTF, Nigga!')


@bot.message_handler(commands=['process'])
def process_responce(message):
    calc = bujda.calculate(int(message.text.replace('/process ','')))
    bot.send_message(message.chat.id,calc)
    bujda.clear()


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
        #print(data)
    except:
        bot.send_message(message.chat.id,
                         'ERROR!\nExpected format X:nnn Y:mmm Z:kkk')
        return

    #print(data)
    storeData(data)
    emptyData = checkFoodData()
    if ['KCal'] in emptyData:
        currentFoodData[
            'KCal'] = currentFoodData['Prot'] * 4 + currentFoodData[
                'Fat'] * 9 + currentFoodData['Carb'] * 4
        emptyData = checkFoodData()

    if emptyData and (emptyData != ['Name']):
        ##print(emptyData)
        for empty in emptyData:
            bot.send_message(message.chat.id, 'Please enter ' + empty)
    else:
        FoodData = calcData(currentFoodData)
        saveData(FoodData)
        status_responce(message)
        #DayFoodData = {'Prot': 0, 'Fat': 0, 'Carb': 0, 'KCal': 0}
        ###print(get_today_stats())
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
