
"""
First, a few callback functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

from dotenv import load_dotenv
import os
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup, 
    ReplyKeyboardRemove,
    Update
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Show Menu", callback_data="cb_menu")],
        [InlineKeyboardButton("Order Drink", callback_data="cb_order")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please choose:", reply_markup=reply_markup)

async def order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    reply_keyboard = [["Drink A", "Drink B", "Drink C", "Drink A", "Drink B"],
                      ["Drink C", "Drink A", "Drink B", "Drink C", "Drink A"],
                      [ "Drink B", "Drink C", "Drink A", "Drink B", "Drink C"]]

    if update.message is not None:
        await update.message.reply_text(
            "Please select what you want to order, or type something for a custom order\nSend /cancel to cancel.\n\n",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="Choose a drink to order"
            ),
        )
    else:
       await update.callback_query.message.reply_text(
            "Please select what you want to order, or type something for a custom order\nSend /cancel to cancel.\n\n",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="Choose a drink to order"
            ),
        ) 

    return 1


async def order_placed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info(f"{user.username} ordered {update.message.text}")
    await update.message.reply_text(
        f"someone ordered {update.message.text}. But who is it?",
        reply_markup=ReplyKeyboardRemove(),
    )

    context.user_data["drink_order"] = update.message.text

    return 2

async def order_customer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    logger.info(f"{user.username} ordered {update.message.text}")
    await update.message.reply_text(
        f"Entering {update.message.text}'s {context.user_data["drink_order"]} into the database"
    )

async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the photo and asks for a location."""
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    await photo_file.download_to_drive("user_photo.jpg")
    logger.info("Photo of %s: %s", user.first_name, "user_photo.jpg")
    await update.message.reply_text(
        "Gorgeous! Now, send me your location please, or send /skip if you don't want to."
    )

    return LOCATION


async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Skips the photo and asks for a location."""
    user = update.message.from_user
    logger.info("User %s did not send a photo.", user.first_name)
    await update.message.reply_text(
        "I bet you look great! Now, send me your location please, or send /skip."
    )

    return LOCATION


async def location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the location and asks for some info about the user."""
    user = update.message.from_user
    user_location = update.message.location
    logger.info(
        "Location of %s: %f / %f", user.first_name, user_location.latitude, user_location.longitude
    )
    await update.message.reply_text(
        "Maybe I can visit you sometime! At last, tell me something about yourself."
    )

    return BIO


async def skip_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Skips the location and asks for info about the user."""
    user = update.message.from_user
    logger.info("User %s did not send a location.", user.first_name)
    await update.message.reply_text(
        "You seem a bit paranoid! At last, tell me something about yourself."
    )

    return BIO


async def bio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the info about the user and ends the conversation."""
    user = update.message.from_user
    logger.info("Bio of %s: %s", user.first_name, update.message.text)
    await update.message.reply_text("Thank you! I hope we can talk again some day.")

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(f"The menu is a b c de.")
    #await query.edit_message_text(text=f"The menu is a b c de.")

def main() -> None:
    load_dotenv(".env")
    BOT_TOKEN = os.environ.get('BOT_TOKEN')

    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(BOT_TOKEN).concurrent_updates(False).build()


    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(show_menu, pattern="cb_menu"))
    
    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("order", order), CallbackQueryHandler(order, pattern="cb_order")],
        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_placed)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_customer)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()