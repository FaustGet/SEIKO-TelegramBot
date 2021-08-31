import telebot

keyboardLanguage = telebot.types.ReplyKeyboardMarkup(True)
keyboardLanguage.row("Русский 🇷🇺")
keyboardLanguage.row("Ўзбекча 🇺🇿")

keyboardStartRU = telebot.types.ReplyKeyboardMarkup(True)
keyboardStartRU.row('Узнать что есть на складе')
keyboardStartRU.row('Информация о линзах')
keyboardStartRU.row('Авторизироваться в системе')
keyboardStartRU.row('Перейти в корзину')
keyboardStartRU.row("Выйти из системы")
keyboardStartRU.row("Сменить язык")

keyboardStartUZ = telebot.types.ReplyKeyboardMarkup(True)
keyboardStartUZ.row('Стокда нима бор')
keyboardStartUZ.row('Линзалар ҳақида маълумот')
keyboardStartUZ.row('Тизимга кириш')
keyboardStartUZ.row('Саватга ўтиш')
keyboardStartUZ.row("Тизимдан чиқиш")
keyboardStartUZ.row("Тилини ўзгартириш")


keyboardOfferRU = telebot.types.ReplyKeyboardMarkup(True)
keyboardOfferRU.row('Оформить заказ')
keyboardOfferRU.row('Убрать товары из корзины')
keyboardOfferRU.row("Назад в главное меню")


keyboardOfferUZ = telebot.types.ReplyKeyboardMarkup(True)
keyboardOfferUZ.row('Буюртмани расмийлаштириш')
keyboardOfferUZ.row('Маҳсулотни саватдан олиб ташлаш')
keyboardOfferUZ.row("Бош менюга қайтиш")

keyboardBackRU = telebot.types.ReplyKeyboardMarkup(True)
keyboardBackRU.row("Назад в главное меню")

keyboardBackUZ = telebot.types.ReplyKeyboardMarkup(True)
keyboardBackUZ.row("Бош менюга қайтиш")




