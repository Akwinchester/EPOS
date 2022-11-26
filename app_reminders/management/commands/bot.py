from django.core.management import BaseCommand
from app_reminders.models import tasks
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, CommandHandler, ConversationHandler, CallbackQueryHandler
from miit_project.settings import TOKEN
import logging
# import telegramcalendar
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
import datetime
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# определяем константы этапов разговора
TASK, DESCRIPTION, DEADLINE = range(3)

# словарь с данными для добавления задач
task_data = {}
# словарь этапов выбора даты
list_step = {}
list_step['y'] = "год"
list_step['m'] = 'месяц'
list_step['d'] = 'день'
class Command(BaseCommand):
    help = 'Implemented to Django application telegram bot setup command'

    def handle(self, *args, **kwargs):
        bot = Bot(token=TOKEN)
        updater = Updater(bot=bot)
        start_handler = CommandHandler('start', start)
        information_handler = CommandHandler('information', start)
        add_task_handler = ConversationHandler(

            entry_points=[CommandHandler('add_task', start_add_task)],
            states={
                TASK: [MessageHandler(Filters.text& ~Filters.command, add_task)],
                DESCRIPTION: [MessageHandler(Filters.text& ~Filters.command, add_description)],
                DEADLINE: [MessageHandler(Filters.text& ~Filters.command, add_deadline)]
            },
            fallbacks=[CommandHandler('cancel', cancel)],
        )
        unknown_handler = MessageHandler(Filters.command, unknown)
        button_handler = CallbackQueryHandler(button)

        updater.dispatcher.add_handler(start_handler)
        updater.dispatcher.add_handler(information_handler)
        updater.dispatcher.add_handler(add_task_handler)
        updater.dispatcher.add_handler(button_handler)
        updater.dispatcher.add_handler(unknown_handler)

        updater.start_polling(timeout=120)
        updater.idle()


def start(update, context):
    start_keyboard = [['/add_task',
                       '/information',
                       '/help']]
    start_markup = ReplyKeyboardMarkup(start_keyboard, one_time_keyboard=True)
    context.bot.send_message(update.message.chat_id, 'Шалом')
    context.bot.send_message(update.message.chat_id, 'Чтобы добавить задачу нажми /add_task. Также ты можешь посмотреть возомжности нашего бота - команда /information. Или задать вопрос в нашу техподдержку /help', reply_markup=start_markup)



def start_add_task(update, _):
    update.message.reply_text('Отправь свою задачу следующим сообщением')
    return TASK


def add_task(update, _):
    chat_id = update.message.chat_id
    if not (chat_id in task_data):
        task_data[chat_id] = {}

    task_data[chat_id]['task_text'] = update.message.text
    update.message.reply_text('Хорошо, теперь добавь описание своей задачи. Если не хочешь, можешь пропустить')
    print(task_data)
    return DESCRIPTION


def add_description(update, _):
    chat_id = update.message.chat_id
    task_data[chat_id]['task_description'] = update.message.text

    reply_keyboard = [['Добавить задачу',
                       '/cancel',
                       '/skip']]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

    calendar, step = DetailedTelegramCalendar().build()
    update.message.reply_text(text='Отлично, теперь укажи к какой дате ты должен это сделать. Если сроков нет, можешь пропустить этот этап', reply_markup=markup_key)
    update.message.reply_text(f"Выберете {list_step[step]}", reply_markup=calendar)

    return DEADLINE


def add_deadline(update, _):
    chat_id = update.message.chat_id
    task = tasks(task_text=task_data[chat_id]['task_text'], task_description=task_data[chat_id]['task_description'], deadline=task_data[chat_id]['task_deadline'])
    task.save()

    update.message.reply_text('задача добавлена')
    print(task_data)

    return ConversationHandler.END


def cancel(update, _):
    # определяем пользователя
    user = update.message.from_user
    # Отвечаем на отказ поговорить
    update.message.reply_text(
        'Мое дело предложить - Ваше отказаться'
        ' Будет скучно - пиши.'
    )
    # Заканчиваем разговор.
    return ConversationHandler.END


def unknown(updater, context):
    chat_id = updater.message.chat_id
    context.bot.send_message(chat_id, 'Я не знаю эту команду')


def button(update, _):
    query = update.callback_query
    result, key, step = DetailedTelegramCalendar().process(query.data)

    if not result and key:
        query.edit_message_text(f"Выберете {list_step[step]}", reply_markup=key)
    elif result:
        time_deadline = '00:00'
        date_deadline = result.strftime('%Y-%m-%d')
        task_data[query.message.chat.id]['task_deadline'] = date_deadline + ' ' + time_deadline
        query.edit_message_text(f"Выбранная дата: {result.strftime('%d.%m.%Y')}")
