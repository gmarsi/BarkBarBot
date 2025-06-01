import os 
import sqlite3
import telebot

from BarkBarModels import *
from dotenv import load_dotenv
from peewee import *
from telebot.types import  InlineKeyboardMarkup, InlineKeyboardButton


# Initialize bot
load_dotenv(".env")
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# Initialize db
db = SqliteDatabase('BarkBar.db')
db.connect()


#### Utility functions ####
def is_staff(username):
    staffer = Staff.get_or_none(telegram_handle=username)
    if staffer is None:
        return False
    else:
        return staffer.active

def is_admin(username):
    staffer = Staff.get_or_none(telegram_handle=username)
    if staffer is None:
        return False
    else:
        return staffer.active and staffer.is_admin



#### Bot Commands ####

# "Start" command is the first interaction you see with the bot
@bot.message_handler(commands=['start'])
def main_menu(message):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("See the menu", callback_data="cb_menu"), InlineKeyboardButton("Order a Drink", callback_data="cb_order"))
    bot.send_message(message.chat.id, "Choose an option:", reply_markup=markup)

@bot.message_handler(commands=['admin'])
def admin_menu(message):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("See the menu", callback_data="cb_menu"), InlineKeyboardButton("Order a Drink", callback_data="cb_order"))
    bot.send_message(message.chat.id, "Choose an option:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    match call.data:
        case "cb_menu":
            bot.send_message(call.message.chat.id, "Here's the menu:\nItem stub\nItem stub, etc")
        case "cb_order":
            bot.send_message(call.message.chat.id, "Here's the menu:\nItem stub\nItem stub, etc")


# Manage staff. Staff can use advanced commands, including adding other staff, adding and managing orders, etc
@bot.message_handler(commands=['staff'])
def manage_staff(message):
    if not is_admin(message.from_user.username):
        bot.reply_to(message, f"You must be an admin to manage staff members.")
        return

    args = message.text.split()
    command_descriptions = "Staff commands:\nadd [telegram username]\ntoggle_active [telegram username]\ntoggle_admin [telegram username]\nremove [telegram username]"
    if len(args) == 1:
        bot.reply_to(message, command_descriptions)
    elif len(args) > 3:
        bot.reply_to(message, f"Wrong number of args\n\n{command_descriptions}")
    else:
        match args[1]:
            case "add":
                staffer = Staff.get_or_none(telegram_handle=args[2])
                if staffer is not None:
                    bot.reply_to(message, f"{args[2]} is already on the staff list. Use 'toggle_active' to enable/disable their account.")
                else:
                    staffer = Staff(telegram_handle=args[2])
                    staffer.save()
                    bot.reply_to(message, f"{args[2]} added to staff list")
            case "toggle_active":
                staffer = Staff.get_or_none(telegram_handle=args[2])
                if staffer is None:
                    bot.reply_to(message, f"{args[2]} is not a staffer. Use 'add' to add them")
                else:
                    staffer.active = not staffer.active
                    staffer.save()
                    bot.reply_to(message, f"{args[2]} is now {"active" if staffer.active else "inactive"}")
            case "toggle_admin":
                staffer = Staff.get_or_none(telegram_handle=args[2])
                if staffer is None:
                    bot.reply_to(message, f"{args[2]} is not a staffer. Use 'add' to add them")
                else:
                    staffer.is_admin = not staffer.is_admin
                    staffer.save()
                    bot.reply_to(message, f"{args[2]} is now{"" if staffer.is_admin else " not"} an admin")
            case "remove":
                staffer = Staff.get_or_none(telegram_handle=args[2])
                if staffer is None:
                    bot.reply_to(message, f"{args[2]} is already not a staffer.")
                else:
                    staffer.delete_instance()
                    bot.reply_to(message, f"{args[2]} removed from staff list")
            case _:
                bot.reply_to(message, f"Invalid command\n\n{command_descriptions}")
            


@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, message.text)

####### Run the bot!
bot.infinity_polling()
