from dagan.resources import resource_path

"""
INTERNAL_INFO
"""
DB_FILE = resource_path('dagan.db')

"""
UPV INFO
"""

TOKEN_FILE = resource_path('_tmp_token_file_.json')  # File to save the last token (Used after a reboot)
INFO_EXP_TIME = 300  # Seconds to cache UPV Info

"""
HMI
"""
NEW_LINE = '\r\n'
CLEAN_TEXT_REPLACE = [['#', NEW_LINE], [':s:', ''], ['  ', ' ']]

ALL_INFO_REPLACE = [['\r\n', ''], ['\n', '']]
RESTAURANT_REPLACE = [['Cafetería', ''], ['Cafeteria', ''], ['Cervecería', ''], ['Cerveceria', ''],
                      ['Club Gastronómico', '']]
PRICE_REPLACE = [(' Euros', '€'), (' euros', '€'), ('Euros', '€'), ('euros', '€')]
RESTAURANT_MENU_SEPARATOR = '  >  '

KEYPAD_COLUMNS = 2

MODE = 'Markdown'
PLAIN = 'HTML'
BOLD_START = '*'
BOLD_END = '*'

"""
KEYPAD CALLBACK DATA
"""
CBDATA_START_CMD = 'S'  # Callback data for Start command
CBDATA_INFO_CMD = 'I'  # Callback data for Info command

CBDATA_INFO_REQ = 'F'  # Callback data for a request of info from a restaurant
CBDATA_REP_REQ = 'Q'  # Callback data for a regular restaurant/menu report request
CBDATA_SUBS_REQ = 'B'  # Callback data for a subscription request
CBDATA_UNSUBS_REQ = 'U'  # Callback data for a unsubscription request

CBDATA_RESTAURANT = 'R'  # Value used to identify a restaurant id
CBDATA_MENU = 'M'  # Value used to identify a menu id

CBDATA_PREVIOUS_TYPE = 'P'  # Value used to report the previous message type (request or cmd)

CBDATA_CANCEL = '-'  # Callback data for a cancel request

"""
SUBSCRIPTIONS
"""
THREAD_TIMER_SECONDS = 600  # Second to wait between each execution of the subscription thread

SUBS_WEEKDAY_LIST = range(4)  # Available Days for sending subscriptions 0 Monday - 6 Sunday
SUBS_HOUR_INTERVAL = [12, 15]  # Available hours for sending subscriptions
