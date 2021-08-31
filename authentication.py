from config import db
from config import bot
from dictionary import language

def signin(login:str,pas:str,telegram_id:int,lang):
    try:
        user = db.users.find_one({"login":login,"pas":pas})
        print(user)
        if user:
            db.auth_user.remove({"telegram_id":telegram_id})
            db.auth_user.insert_one({
                "user":user['name'],
                "telegram_id":telegram_id,
                "code":user['code']
            })
            return f"{language[lang]['Вы авторизовались под']} {user['name']}"
        return language[lang]['Ошибка логина или пароля']
    except:
        return language[lang]['Сервер не доступен']

def is_login(telegram_id:int):
    user = db.auth_user.find_one({"telegram_id":telegram_id})
    if user:
        return user
    else:
        return False

def logout(telegram_id:int,lang = "ru"):
    db.auth_user.remove({"telegram_id": telegram_id})
    return language[lang]['Вы успешно вышли из системы']

def auth(message,lang):
    try:
        data = message.text.split()
        bot.send_message(message.chat.id, signin(data[0],data[1],message.from_user.id,lang))
        return
    except:
        return


