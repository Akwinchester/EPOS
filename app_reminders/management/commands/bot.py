from django.core.management import BaseCommand
from app_reminders.models import tasks
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, CommandHandler, ConversationHandler, CallbackQueryHandler
from miit_project.settings import TOKEN
import logging


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# определяем константы этапов разговора
TASK, DESCRIPTION, DEADLINE = range(3)

# словарь с данными для добавления задач
task_data = {}
class Command(BaseCommand):
    help = 'Implemented to Django application telegram bot setup command'

    def handle(self, *args, **kwargs):
        bot = Bot(token=TOKEN)
        updater = Updater(bot=bot)
        start_handler = CommandHandler('start', start)
        unknown_handler = MessageHandler(Filters.command, unknown)
        add_task_handler = ConversationHandler(

            entry_points=[CommandHandler('add_task', start_add_task)],
            states={
                TASK: [MessageHandler(Filters.text& ~Filters.command, add_task)],
                DESCRIPTION: [MessageHandler(Filters.text& ~Filters.command, add_description)],
                DEADLINE: [MessageHandler(Filters.text& ~Filters.command, add_deadline)]
            },
            fallbacks=[CommandHandler('cancel', cancel)],
        )

        updater.dispatcher.add_handler(start_handler)
        updater.dispatcher.add_handler(add_task_handler)
        updater.dispatcher.add_handler(unknown_handler)

        updater.start_polling(timeout=120)
        updater.idle()


def start(update, context):
    context.bot.send_message(update.message.chat_id, 'Шалом')


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

    update.message.reply_text('Отлично, теперь укажи к какой дате ты должен это сделать. Если сроков нет, можешь пропустить этот этап')
    print(task_data)
    return DEADLINE


def add_deadline(update, _):
    chat_id = update.message.chat_id
    time_deadline = '00:00'
    task_data[chat_id]['task_deadline'] = update.message.text + ' ' + time_deadline
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