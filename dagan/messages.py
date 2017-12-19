from telegram import InlineKeyboardMarkup
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton

from dagan.internal_data import labels, dagan_parameters
from dagan.utils import grouper


def send_msg(bot, chat_id, msg_txt, plain_keyboard=None, cols=2, with_cancel=True):
    reply_markup = _prepare_keyboard(plain_keyboard, cols, with_cancel)
    bot.send_message(chat_id=chat_id, text=msg_txt, parse_mode=labels.MODE, reply_markup=reply_markup)


def edit_msg(bot, update, msg_txt, plain_keyboard=None, cols=2, with_cancel=True):
    reply_markup = _prepare_keyboard(plain_keyboard, cols, with_cancel)
    bot.edit_message_text(text=msg_txt, chat_id=update.message.chat_id,
                          message_id=update.message.message_id, parse_mode=labels.MODE, reply_markup=reply_markup)


def reply_msg(update, msg_txt, plain_keyboard=None, cols=2, with_cancel=True):
    reply_markup = _prepare_keyboard(plain_keyboard, cols, with_cancel)
    update.message.reply_text(msg_txt, reply_markup=reply_markup)


def remove_msg(bot, update):
    bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)


def _prepare_keyboard(plain_keyboard, cols, with_cancel):
    if plain_keyboard is not None and plain_keyboard:
        keyboard = grouper(plain_keyboard, cols)
        if None in keyboard[-1]:
            keyboard[-1] = list(keyboard[-1])
            keyboard[-1].remove(None)
        if with_cancel:
            keyboard.append([InlineKeyboardButton(labels.CANCEL_BTN, callback_data=dagan_parameters.CBDATA_CANCEL)])
        return InlineKeyboardMarkup(keyboard)
    else:
        return None
