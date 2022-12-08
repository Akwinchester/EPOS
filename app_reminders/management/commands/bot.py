from django.core.management import BaseCommand
from app_reminders.models import tasks
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, CommandHandler, ConversationHandler, CallbackQueryHandler
from miit_project.settings import TOKEN
import logging
# import telegramcalendar
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
import datetime
from ...models import tasks

from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# определяем константы этапов разговора для добавления задачи
TASK, DESCRIPTION, DEADLINE = range(3)

# определяем константы этапов разговора для авторизации
LOGIN, PASSWORD= range(2)

# словарь с данными для добавления задач
task_data = {}
input_data = {}
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

        input_handler = ConversationHandler(

            entry_points=[CommandHandler('input', start_input)],
            states={
                LOGIN: [MessageHandler(Filters.text & ~Filters.command, input_password)],
                PASSWORD: [MessageHandler(Filters.text & ~Filters.command, finish_input)],
            },
            fallbacks=[CommandHandler('cancel', cancel)],
        )
        unknown_handler = MessageHandler(Filters.command, unknown)
        button_handler = CallbackQueryHandler(button)

        updater.dispatcher.add_handler(start_handler)
        updater.dispatcher.add_handler(information_handler)
        updater.dispatcher.add_handler(add_task_handler)
        updater.dispatcher.add_handler(input_handler)
        updater.dispatcher.add_handler(button_handler)
        updater.dispatcher.add_handler(input_handler)
        updater.dispatcher.add_handler(unknown_handler)

        updater.start_polling(timeout=120)
        updater.idle()


def start(update, context):
    start_keyboard = [['/add_task',
                       '/information',
                       '/help',
                       '/input',]]
    start_markup = ReplyKeyboardMarkup(start_keyboard, one_time_keyboard=True)
    context.bot.send_message(update.message.chat_id, 'Привет')
    context.bot.send_message(update.message.chat_id, 'Чтобы войти в систему нажми /input. Если ты уже авторизован и хочешь добавить задачу, нажми /add_task. Также ты можешь посмотреть возомжности нашего бота - команда /information. Или задать вопрос в нашу техподдержку /help', reply_markup=start_markup)


#начало диалога по входу в бота
def start_input(update, context):
    context.bot.send_message(update.message.chat_id, "Отправь сообщением имя пользователя")
    return LOGIN


def input_password(update, context):
    chat_id = update.message.chat_id
    user_name = update.message.text
    if not (chat_id in input_data):
        input_data[str(chat_id)] = {}
        input_data[str(chat_id)]['login'] = user_name

    if User.objects.filter(username=user_name).exists():
        update.message.reply_text(f'Отлично, пользователь {user_name} найден. Теперь введи пароль. После авторизации, я удалю твое сообщение с паролем. Паранойя, конечно, но так безопаснее')
        return PASSWORD
    else:
        update.message.reply_text(f'Жаль, пользователь {user_name} не найден. Введи комнду /input и начни сначала')
        return ConversationHandler.END


def finish_input(update, context):
    chat_id = update.message.chat_id
    password = update.message.text
    context.bot.delete_message(chat_id, update.message.message_id)
    input_data[str(chat_id)]['password'] = password
    user = authenticate(username=input_data[str(chat_id)]['login'], password=password)
    tasks_user = tasks.objects.all().filter(user=user.id)
    update.message.reply_text('''Поздравляю, ты вошел в систему!!!
Вот твои задачи:''')
    for task in tasks_user:
        context.bot.send_message(update.message.chat_id, str(task.task_text) + ' ' + str(task.deadline))
    return ConversationHandler.END


    # list_data = update.message.text.split('-')
    # user= authenticate(username=list_data[0], password=list_data[1])
    # if User.objects.filter(username=list_data[0]).exists():
    #     context.bot.send_message(update.message.chat_id, f'пользователь {list_data[0]} найден')
    # else:
    #     context.bot.send_message(update.message.chat_id, f'пользователь {list_data[0]} не найден')
    # tasks_user = tasks.objects.all().filter(user=user.id)
    # print(tasks_user)
    # for task in tasks_user:
    #     context.bot.send_message(update.message.chat_id, str(task.task_text) + ' ' + str(task.deadline))
    #     print(task.task_text)
#конец диалога по входу в бота



#Начало диалога по добавлению задачи
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
#конец диалога по добавлению задачи

#обработчик выхода из любого диалога
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
