from django.core.management import BaseCommand
import telebot
from telebot import types
from app_reminders.models import tasks

bot = telebot.TeleBot('1846983248:AAFWEawI9T02ANqUYvXhkSZPKTmgyyJgEeI')
last_comand_user = {}


class Command(BaseCommand):
    help = 'Implemented to Django application telegram bot setup command'

    def handle(self, *args, **kwargs):
        bot.enable_save_next_step_handlers(delay=2) # Сохранение обработчиков
        bot.load_next_step_handlers()								# Загрузка обработчиков
        bot.infinity_polling()


def add_task(data_task):
    task = tasks(task_text=data_task['task_text'], deadline=data_task['date'], task_description=data_task['description'])
    task.save()


@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item_1 = types.KeyboardButton('Добавить задачу')
    markup.add(item_1)
    bot.send_message(message.chat.id, 'Привет. Добавь задачу', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def body(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item_1 = types.KeyboardButton('Добавить задачу')
    markup.add(item_1)


    if message.chat.id in last_comand_user:
        if last_comand_user[message.chat.id]['add_task'] == 1:
            task = tasks(task_text=message.text)
            task.save()



    if message.text == 'Добавить задачу':
        bot.send_message(message.chat.id, 'Введите задачу')
        if not message.chat.id in last_comand_user:
            last_comand_user[message.chat.id] = {}
        last_comand_user[message.chat.id]['add_task'] = 1