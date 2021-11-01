import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
from flask import Flask, request
ApiToken = '2039655062:AAG7gokuNaoV-je_Is9HGU-e_WeVU2N1sic'
bot = telebot.TeleBot(ApiToken)
server = Flask(__name__)


def sendcoins():
    js = requests.get(
        'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1')
    r = js.json()
    message = ''
    for i in r:
        name = i['symbol']
        price = i['current_price']
        marketcap = i['market_cap']
        pricechange = i['price_change_percentage_24h']
        message += f"کوین: {name}\nقیمت: ${price:,.2f}\nمارکت کپ: {marketcap}\nتغییر روزانه: {pricechange}%\n\n"
    return message


def getFearAndGreed():
    response = requests.get('https://alternative.me/crypto/fear-and-greed-index.png')
    file = open("f.png", "wb")
    file.write(response.content)
    file.close()
    js = requests.get('https://api.alternative.me/fng/?limit=1')
    r = js.json()
    fnumber = int(r['data'][0]['value'])
    return fnumber


def getHeatmap():
   pass

def gen_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("قیمت ارز های برتر", callback_data='crypto-prices'),
               InlineKeyboardButton("ورود به دنیای ارز های دیجیتال", callback_data='teach-videos'),
               InlineKeyboardButton("پترن های معروف", callback_data='popular-patterns'),
               InlineKeyboardButton("نقشه بازار", callback_data='heatmap'),
               InlineKeyboardButton("شاخص ترس و طمع", callback_data='fear-greed'))
    return markup


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, 'به ربات bitcoin general خوش آمدید')
    msg = bot.send_message(
        message.chat.id, "یکی از خدمات را انتخاب کنید", reply_markup=gen_markup())


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    try:
        if call.data == "heatmap":
            bot.send_message(call.from_user.id, 'لطفا چند لحظه صبر کنید')
            getHeatmap()
            bot.send_photo(call.from_user.id, photo=open('heatmap.png', 'rb'), caption='نقشه بازار')
        if call.data == "fear-greed":
            bot.send_message(call.from_user.id, 'لطفا چند لحظه صبر کنید')
            n = getFearAndGreed()
            if n >= 50:
                bot.send_photo(call.from_user.id, photo=open('f.png', 'rb'), caption='شاخص ترس و طمع \n' + 'بازار در '
                                                                                                           'طمع هست '
                                                                                                           'مواظب باش'
                                                                                     + '\n' +
                                                                                     f'اندازه شاخص : {n}')
            else:
                bot.send_photo(call.from_user.id, photo=open('f.png', 'rb'),
                               caption='شاخص ترس و طمع\n' + 'بازار تو ترس هست آماده باش از فرصت ها استفاده کنی' + '\n' +
                                       f'اندازه شاخص : {n}')
        if call.data == "crypto-prices":
            msg = sendcoins()
            bot.send_message(call.from_user.id, msg)
    except:
        bot.send_message(call.from_user.id, 'something went wrong try again later')

@server.route('/' + ApiToken, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://bitcoingeneraltelegrambot.herokuapp.com/' + ApiToken)
    bot.polling()
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

