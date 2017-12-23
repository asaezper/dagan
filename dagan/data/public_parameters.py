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
BOLD_START = '*'
BOLD_END = '*'

"""
KEYPAD CALLBACK DATA
"""
CBDATA_START = 'S'
CBDATA_REQUEST = 'Q'  # Callback data for a regular restaurant/menu request
CBDATA_SUBSCRIBE = 'B'
CBDATA_UNSUBSCRIBE = 'U'

CBDATA_RESTAURANT = 'R'
CBDATA_MENU = 'M'
CBDATA_CANCEL = '-'

"""
SUBSCRIPTIONS
"""
THREAD_TIMER_SECONDS = 600  # Second to wait between each execution of the subscription thread

SUBS_WEEKDAY_LIST = range(3)  # Available Days for sending subscriptions 0 Monday - 6 Sunday
SUBS_HOUR_INTERVAL = [12, 15]  # Available hours for sending subscriptions
