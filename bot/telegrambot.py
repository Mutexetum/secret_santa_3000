#myapp/telegrambot.py
# Example code for telegrambot.py module
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram.ext import Updater
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Bot
from django_telegrambot.apps import DjangoTelegramBot
#import strings
import logging
from .helpers import create_user, get_buttons_for_user, are_data_collected, application_closed, get_user_data
from django.conf import settings as settings_conf
from .models import User_s_santa

logger = logging.getLogger(__name__)


GREETING_IF_APPLICATION_OPEN = "Привет!\n\nЯ очень рад приветствовать тебя тут. Если ты зашел сюда, то ты хочешь стать Секретным Сантой кого-то из чатика addmeto & techsparks.Это очень приятно!" 
GREETING_IF_APPLICATION_CLOSED = ""
RULE1 = "Чтобы всё у нас получилось, ты должен ответить на несколько моих вопросов. Они личные, но знай, я забочусь о безопасности твоих данных."
RULE2 = "Ты расскажешь мне, как тебя зовут, откуда ты и что ты хочешь или не хочешь получить в подарок, а я позабочусь о том, чтобы кто-то получил твой адрес и выдал его твоему Санте. А ты получишь адрес того, кого будешь одаривать ты."
RULE3 = "Так как это секрет, то только ты и будешь знать, кто твой подопечный. Пожалуйста, сохрани эту информацию для себя! Иначе никакой магии не получится."

FULL_NAME_REQUEST = "Введите свое полное имя. (ФИО)"
ADDRESS_REQUEST = "Введи свой почтовый адрес включая ФИО. Пожалуйста, введи его в такой форме, как он должен быть написан на посылке/конверте. К сожалению не возможно доставить посылку без ФИО и правильного адреса, поэтому не огорчай своего Санту и сделай всё правильно."
ABOUT_ME_REQUEST = "Расскажи о себе в двух словах, чтобы у деда был контекст"
I_DONT_WANT = "Чтобы не было неприятных сюрпризов, поделись, что бы ты не хотел ни в коем случае получить в подарок от своего Санты. Если ты не любишь розовых единорогов, то это самое время об этом написать."
I_WANT = "А теперь давай о хорошем. Расскажи тут своему Санте о своих предпочтениях, можешь рассказать немного о себе и о том, что тебе по душе."

REGION_REQUEST = "Для решения логистических проблем санты скажи где ты находишься. Выбери из двух вариантов"
READY_TO_SEND_TO = "Куда ты готов отправить подарок"

APPLICATION_CLOSED = "Сезон закрыт, санта примет ваши письма в следующем году"
DATA_CANNOT_BE_EDITED = "Данные уже нельзя изменить"
ALL_DATA_COLLECTED = "Вы заполнили все данные. Можете поменять или посмотреть свои данные"
ALL_DATA_COLLECTED_APP_CLOSED = "Вы заполнили все данные. Можете посмотреть свои данные"

MESSAGE_TO_SANTA = "Введи текст сообщения для санты"
MESSAGE_TO_VNUK = "Введи текст сообщения для внучка/внучки"
MESSAGE_FROM_SANTA = "Вам письмо от санты \n"
MESSAGE_FROM_VNUK = "Вам письмо от внучка/внучки \n"

SANTA_IS_NONE = "Ваш санта еще не выбран"
VNUK_IS_NONE = "Ваш внук/внучка еще не выбран"


FULL_NAME_SAVED = "ФИО {0} успешно сохраненно"
ADDRESS_SAVED = "Aдрес {0} успешно сохранен"
ABOUT_ME_SAVED = "Краткая информация: {0} \nУспешно сохраненна"
I_WANT_SAVED = "Записал что ты хочешь: {0}"
I_DONNT_WANT_SAVED = "Записал что ты не хочешь: {0}"
REGION_RU_SAVED = "Хорошо, записал что ты находишься в РФ"
REGION_NOT_RU_SAVED = "Хорошо, записал что ты находишься не в РФ"

CAN_SEND_TO_RU_SAVED = "Хорошо, записал что ты готов отправить подарок только в РФ"
CAN_SEND_TO_WW_SAVED = "Хорошо, записал что ты готов отправить подарок по всему миру"

HERE_IS_TARGET = "Дорогой Санта вот твой внучок/внучка\n"


def start(bot, update):
    if application_closed():
        update.message.reply_text(APPLICATION_CLOSED)
        return None

    print(update.message.chat.id)
    user_ss, created = create_user(
        update.effective_user.username,
        update.effective_user.id)
    query = update.callback_query
    user_ss.chat_id = update.message.chat.id
    user_ss.save()
    if created:
        update.message.reply_text(GREETING_IF_APPLICATION_OPEN)
        update.message.reply_text(RULE1)
        update.message.reply_text(RULE2)
        update.message.reply_text(RULE3)
        
        keyboard = main_menu_keyboard(update.effective_user.id)
        update.message.reply_text(main_menu_message(),
                                  reply_markup=keyboard)
    else:
        update.message.reply_text("Ты уже стартовал")
        if are_data_collected(update.effective_user.id):
            second_menu(bot, update)
        else:
            main_menu(bot, update)


def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='Help!')


def write_to_santa(bot, update):
    query = update.callback_query
    if update.message is None:
        bot.sendMessage(query.message.chat_id, text=MESSAGE_TO_SANTA)
    else:
        bot.sendMessage(update.message.chat.id, text=MESSAGE_TO_SANTA)
    user_ss, created = create_user(
        update.effective_user.username,
        update.effective_user.id)
    user_ss.next_step = "write_to_santa"
    user_ss.save()


def write_to_vnuk(bot, update):
    query = update.callback_query
    if update.message is None:
        bot.sendMessage(query.message.chat_id, text=MESSAGE_TO_VNUK)
    else:
        bot.sendMessage(update.message.chat.id, text=MESSAGE_TO_VNUK)

    user_ss, created = create_user(
        update.effective_user.username,
        update.effective_user.id)
    user_ss.next_step = "write_to_vnuk"
    user_ss.save()


def input_message(bot, update):

    user_ss, created = create_user(
        update.effective_user.username,
        update.effective_user.id)
    if user_ss.next_step is None or user_ss.next_step == "":
        if are_data_collected(update.effective_user.id):
            second_menu(bot, update)
        else:
            main_menu(bot, update)
    
    if user_ss.next_step == "add_full_name":
        user_ss.full_name = update.message.text
        user_ss.next_step = None
        user_ss.save()
        update.message.reply_text(text=FULL_NAME_SAVED.format(update.message.text))   
        if are_data_collected(update.effective_user.id):
            second_menu(bot, update)
        else:
            main_menu(bot, update)

    elif user_ss.next_step == "add_address":
        user_ss.address = update.message.text
        user_ss.next_step = None
        user_ss.save()
        update.message.reply_text(text=ADDRESS_SAVED.format(update.message.text))   
        if are_data_collected(update.effective_user.id):
            second_menu(bot, update)
        else:
            main_menu(bot, update)

    elif user_ss.next_step == "add_about_me":
        user_ss.about_me = update.message.text
        user_ss.next_step = None
        user_ss.save()
        update.message.reply_text(text=ABOUT_ME_SAVED.format(update.message.text))   
        if are_data_collected(update.effective_user.id):
            second_menu(bot, update)
        else:
            main_menu(bot, update)

    elif user_ss.next_step == "add_i_want":
        user_ss.i_want = update.message.text
        user_ss.next_step = None
        user_ss.save()
        update.message.reply_text(text=I_WANT_SAVED.format(update.message.text))   
        if are_data_collected(update.effective_user.id):
            second_menu(bot, update)
        else:
            main_menu(bot, update)

    elif user_ss.next_step == "add_i_donnot_want":
        user_ss.i_donnot_want = update.message.text
        user_ss.next_step = None
        user_ss.save()
        update.message.reply_text(text=I_DONNT_WANT_SAVED.format(update.message.text))
        if are_data_collected(update.effective_user.id):
            second_menu(bot, update)
        else:
            main_menu(bot, update)

    elif user_ss.next_step == "write_to_santa":
        if user_ss.my_santa is None:
            update.message.reply_text(text=SANTA_IS_NONE)
            user_ss.next_step = None
            user_ss.save()
            return 0
        send_message(user_ss.my_santa, MESSAGE_FROM_VNUK + update.message.text)
        user_ss.next_step = None
        user_ss.save()

    elif user_ss.next_step == "write_to_vnuk":
        if user_ss.im_santa_for is None:
            update.message.reply_text(text=VNUK_IS_NONE)
            user_ss.next_step = None
            user_ss.save()
            return 0
        send_message(user_ss.im_santa_for, MESSAGE_FROM_SANTA + update.message.text)
        user_ss.next_step = None
        user_ss.save()


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

############################ Menus #########################################

def main_menu(bot, update):
    query = update.callback_query
    if update.message is None:
        bot.sendMessage(query.message.chat_id, text=main_menu_message(), reply_markup=main_menu_keyboard(update.effective_user.id))
    else:
        update.message.reply_text(text=main_menu_message(),
                        reply_markup=main_menu_keyboard(update.effective_user.id))

def second_menu(bot, update):
    query = update.callback_query
    message_text = ALL_DATA_COLLECTED
    if application_closed():
        message_text = ALL_DATA_COLLECTED_APP_CLOSED

    if update.message is None:
        bot.sendMessage(query.message.chat_id, text=message_text, reply_markup=second_menu_keyboard())
    else:
        update.message.reply_text(text=message_text,
                        reply_markup=second_menu_keyboard())

def add_full_name(bot, update):
    query = update.callback_query
    if application_closed():
        bot.sendMessage(query.message.chat_id, text=DATA_CANNOT_BE_EDITED)
        second_menu(bot, update)
        return None
    bot.sendMessage(query.message.chat_id, text=FULL_NAME_REQUEST)
    user_ss, created = create_user(
        update.effective_user.username,
        update.effective_user.id)
    user_ss.next_step = "add_full_name"
    user_ss.save()

def add_address(bot, update):
    query = update.callback_query
    if application_closed():
        bot.sendMessage(query.message.chat_id, text=DATA_CANNOT_BE_EDITED)
        second_menu(bot, update)
        return None
    bot.sendMessage(query.message.chat_id, text=ADDRESS_REQUEST)
    user_ss, created = create_user(
        update.effective_user.username,
        update.effective_user.id)
    user_ss.next_step = "add_address"
    user_ss.save()

def add_about_me(bot, update):
    query = update.callback_query
    if application_closed():
        bot.sendMessage(query.message.chat_id, text=DATA_CANNOT_BE_EDITED)
        second_menu(bot, update)
        return None
    bot.sendMessage(query.message.chat_id, text=ABOUT_ME_REQUEST)
    user_ss, created = create_user(
        update.effective_user.username,
        update.effective_user.id)
    user_ss.next_step = "add_about_me"
    user_ss.save()


def add_i_want(bot, update):
    query = update.callback_query
    if application_closed():
        bot.sendMessage(query.message.chat_id, text=DATA_CANNOT_BE_EDITED)
        second_menu(bot, update)
        return None
    bot.sendMessage(query.message.chat_id, text=I_WANT)
    user_ss, created = create_user(
        update.effective_user.username,
        update.effective_user.id)
    user_ss.next_step = "add_i_want"
    user_ss.save()


def add_i_donnot_want(bot, update):
    query = update.callback_query
    if application_closed():
        bot.sendMessage(query.message.chat_id, text=DATA_CANNOT_BE_EDITED)
        second_menu(bot, update)
        return None
    bot.sendMessage(query.message.chat_id, text=I_DONT_WANT)
    user_ss, created = create_user(
        update.effective_user.username,
        update.effective_user.id)
    user_ss.next_step = "add_i_donnot_want"
    user_ss.save()

def add_my_region(bot, update):
    query = update.callback_query
    if application_closed():
        bot.sendMessage(query.message.chat_id, text=DATA_CANNOT_BE_EDITED)
        second_menu(bot, update)
        return None
    bot.sendMessage(query.message.chat_id, text=REGION_REQUEST, reply_markup=my_region_keyboard())

    user_ss, created = create_user(
        update.effective_user.username,
        update.effective_user.id)
    user_ss.next_step = "add_my_region"
    user_ss.save()


def my_region_0(bot, update):
    query = update.callback_query
    if application_closed():
        bot.sendMessage(query.message.chat_id, text=DATA_CANNOT_BE_EDITED)
        second_menu(bot, update)
        return None
    user_ss, created = create_user(
        update.effective_user.username,
        update.effective_user.id)
    user_ss.my_region = 0
    user_ss.next_step = None
    user_ss.save()
    bot.sendMessage(query.message.chat_id, text=REGION_RU_SAVED)
    if are_data_collected(update.effective_user.id):
        second_menu(bot, update)
    else:
        main_menu(bot, update)


def my_region_1(bot, update):
    query = update.callback_query
    if application_closed():
        bot.sendMessage(query.message.chat_id, text=DATA_CANNOT_BE_EDITED)
        second_menu(bot, update)
        return None
    user_ss, created = create_user(
        update.effective_user.username,
        update.effective_user.id)
    user_ss.my_region = 1
    user_ss.next_step = None
    user_ss.save()
    bot.sendMessage(query.message.chat_id, text=REGION_NOT_RU_SAVED)
    if are_data_collected(update.effective_user.id):
        second_menu(bot, update)
    else:
        main_menu(bot, update)


def add_ready_to_send_to(bot, update):
    query = update.callback_query
    if application_closed():
        bot.sendMessage(query.message.chat_id, text=DATA_CANNOT_BE_EDITED)
        second_menu(bot, update)
        return None
    bot.sendMessage(query.message.chat_id, text=READY_TO_SEND_TO, reply_markup=send_to_region_keyboard())

    user_ss, created = create_user(
        update.effective_user.username,
        update.effective_user.id)
    user_ss.next_step = "add_ready_to_send_to"
    user_ss.save()


def sent_to_region_0(bot, update):
    query = update.callback_query
    if application_closed():
        bot.sendMessage(query.message.chat_id, text=DATA_CANNOT_BE_EDITED)
        second_menu(bot, update)
        return None
    user_ss, created = create_user(
        update.effective_user.username,
        update.effective_user.id)
    user_ss.ready_to_send_to = 0
    user_ss.next_step = None
    user_ss.save()
    bot.sendMessage(query.message.chat_id, text=CAN_SEND_TO_RU_SAVED)
    if are_data_collected(update.effective_user.id):
        second_menu(bot, update)
    else:
        main_menu(bot, update)


def sent_to_region_1(bot, update):
    query = update.callback_query
    if application_closed():
        bot.sendMessage(query.message.chat_id, text=DATA_CANNOT_BE_EDITED)
        second_menu(bot, update)
        return None
    user_ss, created = create_user(
        update.effective_user.username,
        update.effective_user.id)
    user_ss.ready_to_send_to = 1
    user_ss.next_step = None
    user_ss.save()

    bot.sendMessage(query.message.chat_id, text=CAN_SEND_TO_WW_SAVED)
    if are_data_collected(update.effective_user.id):
        second_menu(bot, update)
    else:
        main_menu(bot, update)


def show_my_data(bot, update):
    query = update.callback_query
    data = get_user_data(update.effective_user.id)
    bot.send_message(
        chat_id=query.message.chat_id,
        text=data, 
        parse_mode=ParseMode.MARKDOWN)

############################ Keyboards #########################################
def main_menu_keyboard(user_id):
    buttons, data_collected = get_buttons_for_user(user_id)
    keyboard = []

    for button in buttons:
        keyboard.append([
            InlineKeyboardButton(button['title'], callback_data=button['callback_data'])
            ])

    return InlineKeyboardMarkup(keyboard)

def second_menu_keyboard():

    keyboard = [[InlineKeyboardButton('Посмотреть мои данные', callback_data='SHOW_MY_DATA')]]

    if application_closed() is False:
        keyboard.append([InlineKeyboardButton('Изменить мои данные', callback_data='main')])
    return InlineKeyboardMarkup(keyboard)

def my_region_keyboard():
    keyboard = [[InlineKeyboardButton('РФ', callback_data='REGION_0')],
              [InlineKeyboardButton('Не РФ (EU, USA, etc.)', callback_data='REGION_1')],
              ]
    return InlineKeyboardMarkup(keyboard)

def send_to_region_keyboard():
    keyboard = [[InlineKeyboardButton('Только РФ', callback_data='S_REGION_0')],
              [InlineKeyboardButton('По всему миру', callback_data='S_REGION_1')],
              ]
    return InlineKeyboardMarkup(keyboard)

def messaging_keyboard():
    keyboard = [[InlineKeyboardButton('Написать санте', callback_data='write_to_santa')],
              [InlineKeyboardButton('Написать внучку/внучке', callback_data='write_to_vnuk')],
              ]
    return InlineKeyboardMarkup(keyboard)

############################# Messages #########################################
def main_menu_message():
    return 'Выберите пункт меню чтобы заполнить данные'

############################# Actions #########################################


def send_message(user, message):
    bot = Bot(settings_conf.TELEGRAM_TOKEN)
    bot.send_message(
        chat_id=user.chat_id,
        text=message,
         reply_markup=messaging_keyboard()
        )
    return 0


def send_userinfo_to_santas():
    users = User_s_santa.objects.all()
    bot = Bot(settings_conf.TELEGRAM_TOKEN)

    for user in users:
        if user.my_santa is not None and user.user_id is not None and user.user_id != "":
            data = get_user_data(user.user_id)
            message = HERE_IS_TARGET + data
            try:
                bot.send_message(
                    chat_id=user.my_santa.chat_id,
                    text=message,
                    reply_markup=messaging_keyboard(),
                    parse_mode=ParseMode.MARKDOWN)
            except:
                pass
            
    return 0


def main():
    logger.info("Loading handlers for telegram bot")

    # Default dispatcher (this is related to the first bot in settings.DJANGO_TELEGRAMBOT['BOTS'])
    dp = DjangoTelegramBot.dispatcher
    # To get Dispatcher related to a specific bot
    # dp = DjangoTelegramBot.getDispatcher('BOT_n_token')     #get by bot token
    # dp = DjangoTelegramBot.getDispatcher('BOT_n_username')  #get by bot username

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    dp.add_handler(CommandHandler("write_to_santa", write_to_santa))
    dp.add_handler(CommandHandler("write_to_vnuk", write_to_vnuk))
    dp.add_handler(CallbackQueryHandler(write_to_santa, pattern='write_to_santa'))
    dp.add_handler(CallbackQueryHandler(write_to_vnuk, pattern='write_to_vnuk'))


    dp.add_handler(CallbackQueryHandler(main_menu, pattern='main'))
    dp.add_handler(CallbackQueryHandler(show_my_data, pattern='SHOW_MY_DATA'))
    
    dp.add_handler(CallbackQueryHandler(add_full_name, pattern='add_full_name'))
    dp.add_handler(CallbackQueryHandler(add_full_name, pattern='edit_full_name'))
    
    dp.add_handler(CallbackQueryHandler(add_address, pattern='add_address'))
    dp.add_handler(CallbackQueryHandler(add_address, pattern='edit_address'))
    
    dp.add_handler(CallbackQueryHandler(add_about_me, pattern='add_about_me'))
    dp.add_handler(CallbackQueryHandler(add_about_me, pattern='edit_about_me'))

    dp.add_handler(CallbackQueryHandler(add_i_want, pattern='add_i_want'))
    dp.add_handler(CallbackQueryHandler(add_i_want, pattern='edit_i_want'))

    dp.add_handler(CallbackQueryHandler(add_i_donnot_want, pattern='add_i_donnot_want'))
    dp.add_handler(CallbackQueryHandler(add_i_donnot_want, pattern='edit_i_donnot_want'))

    dp.add_handler(CallbackQueryHandler(add_my_region, pattern='add_my_region'))
    dp.add_handler(CallbackQueryHandler(add_my_region, pattern='edit_my_region'))

    dp.add_handler(CallbackQueryHandler(my_region_0, pattern='REGION_0'))
    dp.add_handler(CallbackQueryHandler(my_region_1, pattern='REGION_1'))

    dp.add_handler(CallbackQueryHandler(add_ready_to_send_to, pattern='add_ready_to_send_to'))
    dp.add_handler(CallbackQueryHandler(add_ready_to_send_to, pattern='edit_ready_to_send_to'))

    dp.add_handler(CallbackQueryHandler(sent_to_region_0, pattern='S_REGION_0'))
    dp.add_handler(CallbackQueryHandler(sent_to_region_1, pattern='S_REGION_1'))

    # dp.add_handler(CallbackQueryHandler(second_menu, pattern='m2'))
    # dp.add_handler(CallbackQueryHandler(first_submenu,
    #                                                 pattern='m1_1'))
    # dp.add_handler(CallbackQueryHandler(second_submenu,
    #                                                 pattern='m2_1'))

    dp.add_handler(MessageHandler(Filters.text, input_message))

    # log all errors
    dp.add_error_handler(error)