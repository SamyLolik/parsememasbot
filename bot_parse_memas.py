import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
import logging
import random
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Приветствие"""
    update.message.reply_text('Напиши мне /cat или /dog и я поделюсь ими с тобой')


def help(bot, update):
    """Сообщение для помощи с командами"""
    update.message.reply_text('Чтобы получить котика напиши /cat')


def echo(bot, update):
    """На любой текст отвечаем ошибкой"""
    update.message.reply_text("Неизвестная команда :(")


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def getcat():
    '''Получение ссылки на картинку с котиком'''
    try:
        r = requests.get('http://thecatapi.com/api/images/get?format=src')
        url = r.url
    except:
        url = 'default_cat.jpg'
        print('Error with cat parsing')
        pass
    return url


def getdog():
    '''Получение ссылки на gif с собачкой'''
    try:
        r = requests.get('https://api.thedogapi.com/v1/images/search?format=src&mime_types=image/gif')
        url = r.url
    except:
        url = 'default_cat.jpg'
        print('Error with dog parsing')
        pass
    return url


def sendcat(bot, update):
    """Отправка котиков"""
    bot.sendPhoto(chat_id=update.message.chat_id, photo=getcat(), reply_markup=draw_button())


def senddog(bot, update):
    """Отправка псин"""
    requests.get('https://api.telegram.org/bot688587980:AAEq-SxRkJ-xd_qOgOeqdumdO39VLA8kISk/sendAnimation?animation={}&chat_id={}'.format(getdog(),update.message.chat_id))
    bot.sendMessage(chat_id=update.message.chat_id, text='Собакен', reply_markup=draw_button())


def send_memas(bot, update):
    data = parse_2ch()
    if data['type'] == 'photo':
        bot.sendPhoto(photo=data['url'], chat_id=update.message.chat_id, reply_markup=draw_button())
    elif data['type'] == 'video':
        bot.sendVideo(video=data['url'], chat_id=update.message.chat_id, reply_markup=draw_button())


def parse_2ch():
    rand = random.randint(1, 9)
    data = {}
    r = requests.get('https://2ch.hk/b/{}.json'.format(rand)).json()
    for posts in r['threads']:
        #posts = random.choice(posts)
        for files in posts['posts']:
            files = files['files']
            random.shuffle(files)
            for path in files:
                if path['path'].endswith('jpg') or path['path'].endswith('png'):
                    data = {'url': 'https://2ch.hk{}'.format(path['path']), 'type': 'photo'}
                    break
                elif path['path'].endswith('mp4') or path['path'].endswith('webm'):
                    data = {'url': 'https://2ch.hk{}'.format(path['path']), 'type': 'video'}
                    break
    return data


def draw_button():
    keys =[[InlineKeyboardButton('🐈Еще котика?!🐈', callback_data='1')],
           [InlineKeyboardButton('Еще собакенов?', callback_data='2')],
           [InlineKeyboardButton('Рандомный мемасик?', callback_data='3')]]
    return InlineKeyboardMarkup(inline_keyboard=keys)


def get_callback_from_button(bot, update):
    query = update.callback_query
    username = update.effective_user.username
    chat_id = query.message.chat.id
    message_id = query.message.message_id
    if int(query.data) == 1:
        bot.sendPhoto(photo=getcat(), chat_id=chat_id, message_id=message_id, reply_markup=draw_button())
    elif int(query.data) == 2:
        requests.get(
            'https://api.telegram.org/bot688587980:AAEq-SxRkJ-xd_qOgOeqdumdO39VLA8kISk/sendAnimation?animation={}&chat_id={}'.format(
                getdog(), chat_id))
        bot.sendMessage(chat_id=chat_id, text='Собакен', reply_markup=draw_button())
    elif int(query.data) == 3:
        data = parse_2ch()
        if data['type'] == 'photo':
            bot.sendPhoto(photo=data['url'], chat_id=chat_id, message_id=message_id, reply_markup=draw_button())
        elif data['type'] == 'video':
            bot.sendVideo(video=data['url'], chat_id=chat_id, message_id=message_id, reply_markup=draw_button())


def send_pidr(bot, update):
    '''пидр функция'''
    users = ['303280312', '414342044', '327884751']
    new_updates = bot.getChatMember(chat_id=update.message.chat_id, user_id=random.choice(users))
    name = new_updates['result']['user']['first_name']
    bot.sendMessage(chat_id=update.message.chat_id, text='Сейчас пидр у нас {}'.format(name))


def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater("688587980:AAEq-SxRkJ-xd_qOgOeqdumdO39VLA8kISk")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    dp.add_handler(CallbackQueryHandler(get_callback_from_button))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("cat", sendcat))
    dp.add_handler(CommandHandler("dog", senddog))
    dp.add_handler(CommandHandler("memas", send_memas))
    dp.add_handler(CommandHandler("пидр", send_pidr))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
