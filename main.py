
import telebot
from authentication import *
from utils import *
from keyboards import *
from config import bot,db
from dictionary import language
LoadInfo()

@bot.message_handler(regexp="^Ўзбекча 🇺🇿?")
def start_command(message):
    bot.send_message(message.chat.id, 'Хайрли кун, сиз линзалар мавжудлигини текшириш учун бот томонидан кутиб олинади',
                     reply_markup=keyboardStartUZ)

@bot.message_handler(regexp="^Русский 🇷🇺?")
def start_command(message):
    bot.send_message(message.chat.id, 'Добрый день, вас приветствует бот по проверке наличия линз',
                     reply_markup=keyboardStartRU)


@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, 'Выберите язык/Тил танлаш', reply_markup=keyboardLanguage)



@bot.message_handler(regexp="^/command2?")
def new_post(message):
    print(message.from_user.username)
    if message.from_user.username == "better_call":
        mes = bot.send_message(message.chat.id, 'Введите новый пост\nНапишите "Меню" чтобы отменить отправку поста')
        bot.register_next_step_handler(mes, add_new_post)

@bot.message_handler(regexp="^/subsscribers?")
def subsscribers(message):
    count = db.subscribers.find().count()
    bot.send_message(message.chat.id, f'Всего активных пользователей - {count}')

@bot.message_handler(regexp="^/orders?")
def order_history(message):
    keyboardUsers= telebot.types.ReplyKeyboardMarkup(True)
    for post in db.users.find():
        keyboardUsers.row(post['name'])
    keyboardUsers.row("Назад в главное меню")
    mes = bot.send_message(message.chat.id, 'Выберите пользователя',reply_markup=keyboardUsers)
    bot.register_next_step_handler(mes, orderHistory)

#обработчик главного меню на двух языках
@bot.message_handler(content_types=['text'])
def send_text(message):
    subscribers = db.subscribers.find_one({"id_user": message.chat.id})
    if not subscribers:
        db.subscribers.insert_one({"id_user": message.chat.id, "user_name": message.from_user.username})

    # обработка на руском языке
    if message.text == 'Узнать что есть на складе':
        text = language['ru'][message.text]
        mes = bot.send_message(message.chat.id,text,reply_markup=keyboardBackRU)
        bot.register_next_step_handler(mes,get_stock_availability,"ru")
        return

    if message.text == "Авторизироваться в системе":
        text = language['ru'][message.text]
        mes = bot.send_message(message.chat.id, text)
        bot.register_next_step_handler(mes,auth,"ru")
        return

    if message.text == "Перейти в корзину":
        current_user = is_login(message.from_user.id)
        if current_user:
            try:
                offer = get_shopping_cart(current_user)
                if offer == 'Корзина пуста':
                    bot.send_message(message.chat.id, 'Корзина пуста')
                    return
                mes = bot.send_message(message.chat.id, offer,reply_markup=keyboardOfferRU)
                bot.register_next_step_handler(mes,add_offer,"ru")
                return
            except:
                bot.send_message(message.chat.id, 'Корзина пуста')
                return
        else:
            bot.send_message(message.chat.id, f'Вы не авторизованны')
            return
    if message.text == "Выйти из системы":
        bot.send_message(message.chat.id, logout(message.from_user.id))
        return

    if message.text == 'Информация о линзах':

        for post in Keybord.list_keyboard:
            if post.get('name') == "Информация о линзах":
                mes = bot.send_message(message.chat.id, 'Узнать информацию о линзах',reply_markup=post.get('value'))
                bot.register_next_step_handler(mes, LensInfo)
                return

    if message.text == "Назад в главное меню":
        bot.send_message(message.chat.id, text=message.text, reply_markup=keyboardStartRU)
        return

    #обработка на узбекистанском языке

    if message.text == "Стокда нима бор":
        text = language['uz'][message.text]
        mes = bot.send_message(message.chat.id, text, reply_markup=keyboardBackUZ)
        bot.register_next_step_handler(mes, get_stock_availability,"uz")
        return

    if message.text == "Тизимга кириш":
        text = language['uz'][message.text]
        mes = bot.send_message(message.chat.id, text)
        bot.register_next_step_handler(mes, auth,"uz")
        return


    if message.text == "Тизимдан чиқиш":
        bot.send_message(message.chat.id, logout(message.from_user.id,"uz"))
        return


    if message.text == 'Линзалар ҳақида маълумот':
        for post in KeybordUZ.list_keyboard:
            if post.get('name') == "Линзалар ҳақида маълумот":
                mes = bot.send_message(message.chat.id, 'Линза ҳақида маълумот топиш',reply_markup=post.get('value'))
                bot.register_next_step_handler(mes,LensInfo,'uz')
                return

    if message.text == "Бош менюга қайтиш":
        bot.send_message(message.chat.id, text=message.text, reply_markup=keyboardStartUZ)
        return

    if message.text == "Саватга ўтиш":
        current_user = is_login(message.from_user.id)
        if current_user:
            try:
                offer = get_shopping_cart(current_user,"uz")
                if offer == 'Сават бўш':
                    bot.send_message(message.chat.id, 'Сават бўш')
                    return
                mes = bot.send_message(message.chat.id, offer,reply_markup=keyboardOfferUZ)
                bot.register_next_step_handler(mes,add_offer,"uz")
                return
            except:
                bot.send_message(message.chat.id, 'Сават бўш')
                return
        else:
            bot.send_message(message.chat.id, f'Сиз тизимга кирмадингиз')
            return


#------------------------------------
    if message.text == "Сменить язык" or message.text == 'Тилини ўзгартириш':
        bot.send_message(message.chat.id, 'Тил танлаш/Выберите язык', reply_markup=keyboardLanguage)
        return

    message_text = check_lens(message,'ru')
    if message_text:
        mes = bot.send_message(message.chat.id, text=message_text,parse_mode="Markdown")
        return
    bot.send_message(message.chat.id, 'Главное меню', reply_markup=keyboardStartRU)



bot.polling(True)
