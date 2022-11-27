import json
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pathlib import Path
import logging
import os

parent_directory = str(Path().absolute())

with open(parent_directory + '/telegram/config.json') as config_file:
    data = json.load(config_file)

log_file = parent_directory + '/logs/mc-logs-full.log'
logging.basicConfig(
    filename=log_file,
    filemode='a',
    format='[%(asctime)s] {%(name)s}: %(levelname)s: %(message)s',
    datefmt='%m/%d/%Y %H:%M:%S',
    level=logging.INFO
)
logger = logging.getLogger("TG")

bot = telebot.AsyncTeleBot(data['bot_token'], parse_mode="HTML")
main_chat_id = data['main_chat_id']
test_chat_id = data['test_chat_id']
        

@bot.message_handler(commands=['help'])
def send_help(message: Message) -> None:
    answer = """
    Помощь по командам:
* /start   - проверить работу бота
* /getID   - получить свой ID
* /restart - перезапустить бота
    """

    bot.send_message(message.chat.id, answer)


@bot.message_handler(commands=['start'])
def simpleAnswer(message: Message) -> None:
    bot.reply_to(message, "Hey, works fine!")


@bot.message_handler(commands=['getID'])
def sendChatID(message: Message) -> None:
    bot.send_message(message.chat.id, "Your ID is: " + str(message.from_user.id))

@bot.message_handler(commands=['restart'])
def restartApp(message: Message) -> None:
    try:
        os.system('service supervisor restart')
        logger.info("Restarting supervisor")
        bot.send_message(message.chat.id, "App was restarted!")
    except:
        logger.error("Error restarting supervisor")
        bot.send_message(message.chat.id, "Error restarting App!")


def sendMessage(message: str) -> None:
    bot.send_message(main_chat_id, message)


def sendMessageTest(message: str) -> None:
    bot.send_message(test_chat_id, message)



# sending message with inlinekeyboard

# keyboard buttons should generate from change_reasons tables
# regarding change_action
# callback_data also from that table

def gen_markup(reasons):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    
    for r in reasons:
        r_type = list(r.keys())[0]
        r_text = list(r.values())[0]
        markup.add(InlineKeyboardButton(r_text, callback_data=r_type))

    # markup.add(InlineKeyboardButton("Yes", callback_data="cb_yes"),
                            #    InlineKeyboardButton("No", callback_data="cb_no"))
    return markup


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "quality_issue":
        
        bot.answer_callback_query(call.id, "Answer is Yes")
    elif call.data == "cb_no":
        bot.answer_callback_query(call.id, "Answer is No")


# @bot.message_handler(func=lambda message: True)
# def message_handler(message):
#     bot.send_message(message.chat.id, "Yes/no?", reply_markup=gen_markup())


def sendMessageKeyboard(message, reasons):
    bot.send_message(test_chat_id, message, reply_markup=gen_markup(reasons))

def startPolling():
    bot.polling()
