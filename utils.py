import json
import datetime
import re
import telebot
from dictionary import language
from authentication import is_login
from config import db, bot
from keyboards import *
from xml_parser import add_new_order, ParseCS, get_Nomenclature, ParseDoubleCS


class Keybord(object):
    list_keyboard = []
    value = {}


class KeybordUZ(object):
    list_keyboard = []
    value = {}


def get_orderHistory(mes,user,lang="ru"):
    try:
        dateFrom = mes.text.split("-")[0].split(".")
        dateTo = mes.text.split("-")[1].split(".")
        dateFromTS= int(datetime.datetime.timestamp(datetime.datetime(int(dateFrom[2]),
                                                                      int(dateFrom[1]),
                                                                      int(dateFrom[0]))))
        dateToTS = int(datetime.datetime.timestamp(datetime.datetime(int(dateTo[2]),
                                                                     int(dateTo[1]),
                                                                     int(dateTo[0]),23,59,59)))
        order = db.order_history.find({"code_partner":user['code'],"date_timestamp":{"$gte": dateFromTS, "$lt": dateToTS}})
        if order.count() == 0:
            bot.send_message(mes.chat.id, text=language[lang]['Нет заказов'])
            return
        list_order = f"{language[lang]['История заказов']}:\n"
        for post in order:

            list_order += f'{datetime.datetime.fromtimestamp(post["date_timestamp"]).strftime("%Y-%m-%d %H:%M:%S")}\n'
            for items in post['order']:
                list_order += f'{items["name"]}-{items["amount"]}\n'
        bot.send_message(mes.chat.id, text=list_order)
        return
    except:
        bot.send_message(mes.chat.id, text=language[lang]['Повторите запрос'])
        return

def orderHistory(message):
    if message.text == "Назад в главное меню":
        bot.send_message(message.chat.id, text=message.text, reply_markup=keyboardStartRU)
        return

    user = db.users.find_one({"name":message.text})
    if user:
        mes = bot.send_message(message.chat.id, text='Введите временной период ДД.ММ.ГГГГ-ДД.ММ.ГГГГ\n'
                                               'Например: 01.01.2021-01.02.2021')
        bot.register_next_step_handler(mes, get_orderHistory,user)

    bot.register_next_step_handler(message,orderHistory)




def get_text(list_lens,find,lang = "ru"):
    if find == 0:
        return f'{language[lang]["На складе нет таких линз"]}\n'
    else:
        if find == -1:
            return f'{language[lang]["Cклад обновляется, проведите запрос чуть позже"]}\n'
        else:
            if list_lens:
                text = ""
                for post in list_lens:
                    text = text + post+"\n"
                return text
    return

def get_KeyboardShoppingCart(current_user,lang = "ru"):
    shopping_cart = db.users.find_one({"name": current_user['user']})['shopping cart']
    if not shopping_cart:
        return
    keyboardSC = telebot.types.ReplyKeyboardMarkup(True)
    for index in range(len(shopping_cart)):
        keyboardSC.row(f'{index+1}. {shopping_cart[index]["name"]}')
    keyboardSC.row(language[lang]['Очистить все'])
    keyboardSC.row(language[lang]['Вернуться в корзину'])
    return keyboardSC

def delete_item(item:str,current_user):
    try:
        shopping_cart = db.users.find_one({"name": current_user['user']})['shopping cart']
        del_item = shopping_cart[int(item[:item.find('.')])-1]
        if del_item['name'] == item[item.find('.')+2:]:
            amount = del_item['amount'] - 1
            if amount == 0:
                db.users.update_one({"name": current_user['user']},
                                   {"$pull":{'shopping cart':{"Code":del_item['Code']}}})

            else:
                db.users.update_one({"name": current_user['user'], "shopping cart.Code": del_item['Code']},
                                    {"$set": {"shopping cart.$.amount": amount}})
            return 1
        return 0
    except:
        return 0

def get_shopping_cart(current_user,lang = "ru"):
    s_cart = db.users.find_one({"name": current_user['user']})
    if len(s_cart['shopping cart']) == 0:
        return language[lang]['Корзина пуста']
    if lang == "ru":
        offer = f"Заказчик {current_user['user']} \nВ корзине \n"
    else:
        offer = f"Буюртмачи {current_user['user']} \nСаватда жами \n"
    shopping_cart = s_cart['shopping cart']
    for index in range(len(shopping_cart)):
        offer += f"{index+1}. {shopping_cart[index]['name']} {language[lang]['количество']}: {shopping_cart[index]['amount']} \n"
    return offer

def add_offer(message,lang="ru"):
    if message.text == "Назад в главное меню":
        bot.send_message(message.chat.id, text=message.text, reply_markup=keyboardStartRU)
        return
    if message.text == "Бош менюга қайтиш":
        bot.send_message(message.chat.id, text=message.text, reply_markup=keyboardStartUZ)
        return

    current_user = is_login(message.chat.id)

    if message.text == "Убрать товары из корзины" or message.text =="Маҳсулотни саватдан олиб ташлаш":
        KeyboardShoppingCart = get_KeyboardShoppingCart(current_user,lang)
        bot.send_message(message.chat.id, text=language[lang]['Какой товар убрать из корзины?'], reply_markup=KeyboardShoppingCart)

    if message.text == "Оформить заказ" or message.text == "Буюртмани расмийлаштириш":
        if current_user:
            shopping_cart = db.users.find_one({"name":current_user['user']})['shopping cart']
            order = {"user":current_user['user'],
                    "order":shopping_cart,
                    "code_partner":current_user['code'],
                    "date":datetime.datetime.now().strftime('%H:%M - %d.%m.%Y'),
                    'date_timestamp': int((datetime.datetime.now()+datetime.timedelta(hours=5)).timestamp())}
            db.order_history.insert_one(order)
            db.users.update_one({"name": current_user['user']},
                                 {"$set": {"shopping cart": []}})
            add_new_order(order)
            moderator = db.subscribers.find_one({"user_name":"FaustGet"})
            if moderator:            
                user_order = ""
                for item in shopping_cart:
                    user_order += f'{item.get("name")} - {item.get("amount")}\n '             
                moderator_text = f'{current_user["user"]} оформили заказ \n{user_order}'
                bot.send_message(moderator['id_user'], text=moderator_text)
            if lang == "ru":
                bot.send_message(message.chat.id, text="Заказ оформлен", reply_markup=keyboardStartRU)
            else:
                bot.send_message(message.chat.id, text="Буюртма расмийлаштирилди", reply_markup=keyboardStartUZ)
        return

    if message.text == "Вернуться в корзину" or message.text == "Саватга қайтиш":
        offer = get_shopping_cart(current_user)
        if lang == "ru":
            bot.send_message(message.chat.id, offer,reply_markup=keyboardOfferRU)
        else:
            bot.send_message(message.chat.id, offer, reply_markup=keyboardOfferUZ)
        if offer == 'Корзина пуста' or offer == 'Сават бўш':
            return

    if message.text == "Очистить все" or message.text == 'Ҳаммасини тозалаш':
        if current_user:
            db.users.update_one({"name": current_user['user']},
                            {"$set": {"shopping cart": []}})
        if lang == "ru":
            bot.send_message(message.chat.id, "Корзина отчищена", reply_markup=keyboardStartRU)
        else:
            bot.send_message(message.chat.id, "Сават бўш", reply_markup=keyboardStartUZ)

        return

    message_text = check_lens(message,lang)
    if message_text:
        bot.send_message(message.chat.id, text=message_text,parse_mode="Markdown")

    if delete_item(message.text,current_user) == 1:
        bot.send_message(message.chat.id, text=language[lang]['Товар был удален из корзины'])
        offer = get_shopping_cart(current_user,lang)
        if offer == 'Корзина пуста':
            bot.send_message(message.chat.id, offer, reply_markup=keyboardStartRU)
            return
        if offer == 'Сават бўш':
            bot.send_message(message.chat.id, offer, reply_markup=keyboardStartUZ)
            return
        if lang =="ru":
            bot.send_message(message.chat.id, offer, reply_markup=keyboardOfferRU)
        else:
            bot.send_message(message.chat.id,  offer, reply_markup=keyboardOfferUZ)
        KeyboardShoppingCart = get_KeyboardShoppingCart(current_user,lang)
        bot.send_message(message.chat.id, text=language[lang]['Какой товар убрать из корзины?'], reply_markup=KeyboardShoppingCart)
    bot.register_next_step_handler(message,add_offer,lang)


def get_stock_availability(message,lang = "ru",keyb = None,list_keyb ={}):

    if keyb == None:
        keyb = telebot.types.ReplyKeyboardMarkup(True)
    try:
        message_text = f"{language[lang]['На складе были найдены следующие линзы']}:\n"
        message.text = message.text.replace("-0.00", "+0.00")
        message.text = message.text.replace("-0,00", "+0.00")
        message.text = message.text.replace(" 0,00", " +0.00") 
        message.text = message.text.replace(" 0.00", " +0.00")
        if " 0" in message.text:
            message.text = message.text.replace(" 0", " +0.00")
        if message.text == "0" or message.text == "0.00" or message.text == "0,00":
            message.text = "+0.00"
           

        if re.match('^[+-]\d[,.]\d\d? [+-]\d[,.]\d\d?$',message.text):
            text = message.text.replace(",", ".")
            value = text.split()
            keyb = telebot.types.ReplyKeyboardMarkup(True)
            list_lens, find, keyb,list_keyb = ParseCS(value[0], value[1],keyb,lang)
            message_text += get_text(list_lens, find)

            keyb.row(language[lang]['Назад в главное меню'])

        if re.match('^[+-]\d[,.]\d\d?$',message.text):
            text = message.text.replace(",", ".")
            value = text.split()
            keyb = telebot.types.ReplyKeyboardMarkup(True)
            list_lens, find, keyb,list_keyb = ParseCS(value[0], "+0.00",keyb,lang)
            message_text += get_text(list_lens, find)
            keyb.row(language[lang]['Назад в главное меню'])

        if re.match('[+-]\d[,.]\d\d? [+-]\d[,.]\d\d? [+-]\d[,.]\d\d?$', message.text):
            text = message.text.replace(",", ".")
            value = text.split()
            keyb = telebot.types.ReplyKeyboardMarkup(True)
            list_lens, find, keyb,list_keyb = ParseDoubleCS(value[0], value[1], value[2], "+0.00", keyb,lang)
            message_text +=  get_text(list_lens, find)
            keyb.row(language[lang]['Назад в главное меню'])

        if re.match('[+-]\d[,.]\d\d? [+-]\d[,.]\d\d? [+-]\d[,.]\d\d? [+-]\d[,.]\d\d?$', message.text):
            text = message.text.replace(",", ".")
            value = text.split()
            keyb = telebot.types.ReplyKeyboardMarkup(True)
            list_lens, find, keyb,list_keyb = ParseDoubleCS(value[0], value[1], value[2], value[3], keyb,lang)

            message_text +=  get_text(list_lens, find)
            keyb.row(language[lang]['Назад в главное меню'])

        if message.text == "Назад в главное меню":
            bot.send_message(message.chat.id, text=message.text, reply_markup=keyboardStartRU)
            return

        if message.text == "Бош менюга қайтиш":
            bot.send_message(message.chat.id, text=message.text, reply_markup=keyboardStartUZ)
            return

        list_nomenclature_info = get_Nomenclature(message.text,list_keyb)
        list_nomenclature_info=sorted(list_nomenclature_info,key=lambda x:x['Amount'])
        message_text_order = ""
        flag_amount = True

        for nomenclature_info in list_nomenclature_info:
            current_user = is_login(message.from_user.id)
            if current_user:
                partners = db.users.find_one({"name":current_user['user']})
                flag = False

                for post in partners['shopping cart']:
                    if post.get('Code') == nomenclature_info.get('Code') and flag_amount:
                        if int(nomenclature_info.get("Amount")) >= int(post.get('amount') + 1):
                            db.users.update_one({"name":current_user['user'], "shopping cart.Code":nomenclature_info.get("Code")},
                                                {"$set":{"shopping cart.$.amount":post.get('amount') + 1}})
                            flag = True
                            message_text_order += f"{language[lang]['В корзину были добавлены']}:\n{nomenclature_info.get('name')}\n" \
                                                  f"{language[lang]['Всего в корзине']}: {post.get('amount') + 1}\n "
    
                        else:
                            flag = True
                            flag_amount = False
                            message_text_order = language[lang]['В корзине максимальное количество линз данной модели']
                if not flag and flag_amount:
                    items = {"name": nomenclature_info.get("name"),
                             "Code": nomenclature_info.get('Code'),
                             "amount":1}
                    db.users.update_one({"name": current_user['user']},
                                        {"$push": {"shopping cart": items}})
                    message_text_order += f"{language[lang]['В корзину были добавлены']}:\n{nomenclature_info.get('name')}\n" \
                                          f"{language[lang]['Всего в корзине']}: 1\n"
    
    
            else:
                message_text_order = language[lang]['Вы не авторизованны']
        if message_text_order !="":
            message_text = message_text_order
        if message_text == f"{language[lang]['На складе были найдены следующие линзы']}:\n":
            message_text = language[lang]["Введен неправильный формат данных"]

        mes = bot.send_message(message.chat.id,message_text, reply_markup=keyb,parse_mode="Markdown")
        bot.register_next_step_handler(mes,get_stock_availability,lang,keyb,list_keyb)
    except:

        message_text = language[lang]["Введен неправильный формат данных"]

        mes = bot.send_message(message.chat.id, message_text, reply_markup=keyb)
        bot.register_next_step_handler(mes, get_stock_availability,lang, keyb,list_keyb)

def add_new_post(message):
    try:
        if message.text == "Меню":
            return
        if message.content_type == 'photo':
            fileID = message.photo[-1].file_id
            file_info = bot.get_file(fileID)
            downloaded_file = bot.download_file(file_info.file_path)
            for user in db.subscribers.find():
              bot.send_photo(user['id_user'],downloaded_file,caption=message.caption)
        if message.content_type == 'text':
            for user in db.subscribers.find():
              bot.send_message(user['id_user'],message.text)
        return
    except:
        return

def parsJson(data,lang = 'ru'):
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    list_obj = []
    for post in data:
        if "value" in data.get(post):
            k,l = parsJson(data.get(post).get("value"),lang)
            if lang == 'uz':
                KeybordUZ.list_keyboard.append({"name":post,"value":k,"message":l})

            else:
                Keybord.list_keyboard.append({"name": post, "value": k, "message": l})
        keyboard.row(post)
        list_obj.append({"name":post,"value":data.get(post)})
        if len(data.get(post)) != 2:
            if lang == 'uz':
                KeybordUZ.value[post] = data.get(post)
            else:
                Keybord.value[post] = data.get(post)
        if "message" in data.get(post):
            if data.get(post).get('message') != "":
               if lang == 'uz':
                   KeybordUZ.value[post] = data.get(post).get('message')
               else:
                   Keybord.value[post] = data.get(post).get('message')
    return keyboard,list_obj


def LoadInfo():
    with open('JsonLense.json', 'r', encoding='utf-8') as fh:  # открываем файл на чтение
        data = json.load(fh)
    parsJson(data)
    with open('JsonLenseUZ.json', 'r', encoding='utf-8') as fh:  # открываем файл на чтение
        data = json.load(fh)

    parsJson(data,'uz')
    return Keybord.list_keyboard


def LensInfo(message,lang='ru'):
    try:
        if lang == 'uz':
            kb = KeybordUZ
        else:
            kb = Keybord
        if message.text == 'Назад в главное меню':
            bot.send_message(message.chat.id, text="В главное меню", reply_markup=keyboardStartRU)
            return
        if message.text == 'Бош менюга қайтиш':
            bot.send_message(message.chat.id, text="Бош менюга ўтиш", reply_markup=keyboardStartUZ)
            return
        fl = False
        for post in kb.list_keyboard:
            if post.get('name') == message.text and not fl:
                if message.text in kb.value:
                    mes = bot.send_message(message.chat.id, text=kb.value.get(message.text), reply_markup=post.get('value'))
                    fl = True
                else:
                    mes = bot.send_message(message.chat.id,text=message.text, reply_markup=post.get('value'))
                    fl = True

        if message.text in kb.value:
            for post in kb.list_keyboard:
                if post.get('name') == kb.value.get(message.text) and not fl:
                    mes = bot.send_message(message.chat.id, text=kb.value.get(message.text),reply_markup=post.get('value'))
                    fl = True
            if not fl:
                mes = bot.send_message(message.chat.id, text=kb.value.get(message.text))
        message_text = check_lens(message,lang)
        if message_text:
            mes = bot.send_message(message.chat.id, text=message_text,parse_mode="Markdown")
        bot.register_next_step_handler(mes,LensInfo,lang)
    except:
        bot.register_next_step_handler(message,LensInfo,lang)




def check_lens(message,lang):
    try:
        message_text = f"{language[lang]['На складе были найдены следующие линзы']}:\n"
        message.text = message.text.replace("-0.00", "+0.00")
        message.text = message.text.replace("-0,00", "+0.00")
        message.text = message.text.replace(" 0,00", " +0.00") 
        message.text = message.text.replace(" 0.00", " +0.00")
        if " 0" in message.text:
            message.text = message.text.replace(" 0", " +0.00")
        if message.text == "0" or message.text == "0.00" or message.text == "0,00":
            message.text = "+0.00"
        
        keyb = telebot.types.ReplyKeyboardMarkup(True)
        find = 0
        if re.match('^[+-]\d[,.]\d\d? [+-]\d[,.]\d\d?$',message.text):
            text = message.text.replace(",", ".")
            value = text.split()
            list_lens, find, keyb,list_keyb = ParseCS(value[0], value[1],keyb,lang)
            message_text += get_text(list_lens, find)
            if find != 1:
                return f'{language[lang]["На складе нет таких линз"]}\n'


        if re.match('^[+-]\d[,.]\d\d?$',message.text):
            text = message.text.replace(",", ".")
            value = text.split()
            list_lens, find, keyb,list_keyb = ParseCS(value[0], "+0.00",keyb,lang)
            message_text += get_text(list_lens, find)
            if find != 1:
                return f'{language[lang]["На складе нет таких линз"]}\n'
        

        if re.match('[+-]\d[,.]\d\d? [+-]\d[,.]\d\d? [+-]\d[,.]\d\d?$', message.text):
            text = message.text.replace(",", ".")
            value = text.split()
            list_lens, find, keyb,list_keyb = ParseDoubleCS(value[0], value[1], value[2], "+0.00", keyb,lang)
            message_text +=  get_text(list_lens, find)
            if find != 1:
                return f'{language[lang]["На складе нет таких линз"]}\n'
        

        if re.match('[+-]\d[,.]\d\d? [+-]\d[,.]\d\d? [+-]\d[,.]\d\d? [+-]\d[,.]\d\d?$', message.text):
            text = message.text.replace(",", ".")
            value = text.split()
            list_lens, find, keyb,list_keyb = ParseDoubleCS(value[0], value[1], value[2], value[3], keyb,lang)
            message_text +=  get_text(list_lens, find)
            if find != 1:
                return f'{language[lang]["На складе нет таких линз"]}\n'
        if find == 1:
            return message_text
        return False
    except:
        return False