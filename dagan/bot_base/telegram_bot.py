from telegram import InlineKeyboardMarkup, ChatAction
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton

from dagan.data import public_parameters, labels


class TelegramBot:
    """
    TelegramBot Base Bot: Class for a regular Telegram Bot
    """

    def __init__(self, bot):
        self.bot = bot  # API's bot instance (token, basics methods, etc)

    def send_msg(self, chat_id, msg_txt, button_list=None, cols=public_parameters.KEYPAD_COLUMNS, with_cancel=True,
                 parse_mode=public_parameters.MODE):
        """
        Method to send a message

        :param chat_id: Id of chat
        :param msg_txt: Message Text
        :param button_list: List of buttons
        :param cols: Columns to distribute buttons
        :param with_cancel: Add a cancel button (True / False)
        :param parse_mode: Parse Mode
        """
        keypad = self.prepare_keypad(button_list, cols, with_cancel)
        self.bot.send_message(chat_id=chat_id, text=msg_txt, parse_mode=parse_mode, reply_markup=keypad)

    def edit_msg(self, chat_id, msg_id, msg_txt, button_list=None, cols=public_parameters.KEYPAD_COLUMNS,
                 with_cancel=True):
        """
        Method to edit a message

        :param chat_id: Id of conversation
        :param msg_id: Message's id to modify
        :param msg_txt: Message text
        :param button_list: List of buttons
        :param cols: Columns to distribute buttons
        :param with_cancel: Add a cancel button (True / False)
        """
        keypad = self.prepare_keypad(button_list, cols, with_cancel)
        self.bot.edit_message_text(text=msg_txt, chat_id=chat_id, message_id=msg_id, parse_mode=public_parameters.MODE,
                                   reply_markup=keypad)

    def reply_msg(self, chat_id, msg_id, msg_txt, button_list=None, cols=public_parameters.KEYPAD_COLUMNS,
                  with_cancel=True):
        """
        Method to reply to a message

        :param chat_id: Id of conversation
        :param msg_id: Message's id to reply
        :param msg_txt: Message text
        :param button_list: List of buttons
        :param cols: Columns to distribute buttons
        :param with_cancel: Add a cancel button (True / False)
        """
        keypad = self.prepare_keypad(button_list, cols, with_cancel)
        self.bot.send_message(chat_id, msg_txt, reply_to_message_id=msg_id, parse_mode=public_parameters.MODE,
                              reply_markup=keypad)

    def remove_msg(self, chat_id, msg_id):
        """
        Method to remove a message

        :param chat_id: Id of conversation
        :param msg_id: Message's id to remove
        """
        self.bot.delete_message(chat_id=chat_id, message_id=msg_id)

    def send_location(self, chat_id, latitude, longitude):
        self.bot.send_location(chat_id=chat_id, latitude=latitude, longitude=longitude)

    def send_contact(self, chat_id, name, phone):
        self.bot.send_contact(chat_id=chat_id, phone_number=phone, first_name=name)

    def report_busy(self, chat_id):
        self.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    @staticmethod
    def prepare_keypad(button_list, cols, with_cancel):
        """
        Build a keypad for a Telegram's message

        :param button_list: List of buttons
        :param cols: Number of columns
        :param with_cancel: Add a cancel button (True / False)
        """
        if button_list is not None and button_list:
            keypad = TelegramBot.grouper(button_list, cols)  # Group buttons in cols
            if with_cancel:  # Add a cancel button
                keypad.append([InlineKeyboardButton(labels.CANCEL_BTN, callback_data=public_parameters.CBDATA_CANCEL)])
            return InlineKeyboardMarkup(keypad)
        else:
            return None

    @staticmethod
    def grouper(iterable, n):
        """
        Group a list of items in a lists of n items
        :param iterable: initial plain list of item
        :param n: Length of groped list
        :return: List of groupd list of size n
        """
        result = [[]]
        for item in iterable:
            if len(result[-1]) != n:
                result[-1].append(item)
            else:
                result.append([item])
        return result
