from dagan import resource_path

TOKEN_FILE = resource_path('_tmp_token_file_.json')

BAR_REPLACE = ['Cafetería', 'Cafeteria', 'Cervecería', 'Cerveceria', 'Club Gastronómico']

CBDATA_START = '*S*'
CBDATA_BAR = '*B*'
CBDATA_MENU = '*M*'

CBDATA_REQ = '*Q*'
CBDATA_SUBS = '*U*'
CBDATA_REM = '*R*'

CBDATA_CANCEL = str(None)

INFO_EXP_TIME = 300

THREAD_TIMER_SECONDS = 600

SUBS_WEEKDAY_LIST = range(3)  # 0 Monday - 6 Sunday
SUBS_HOUR_INTERVAL = [12, 15]
