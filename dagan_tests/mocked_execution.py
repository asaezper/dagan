import logging
import unittest
from unittest.mock import patch

from dagan.__main__ import main
from dagan.data import public_parameters

TOKEN = '{"access_token": "AAAA", "token_type": "Bearer", "expiration_time": 9999999999}'
INFO_JSON = '[{"ID_BAR":"0","NOMBRE_BAR":"BAR_1","NOMBRE_BAR_V":"BAR_1","NOMBRE_BAR_I":"BAR_1","LONGITUD":"","LATITUD":"","EMAIL_BAR":"","TELEF":"","TELEF_2":"","WEB":"","FECHA":"27/12/2017","MENU":"Ensaladas","PLATO1":"Ensalada de pavo :s:#Ensalada de pavo modificada :s:#Ensalada mediterránea :s:#Ensalada de pasta :s:#Ensalada con nueces :s:#Ensalada de garbanzos:s:#Ensalada de frutas :s:","PLATO2":"","OTROS":"","OBSERVACIONES":"","HORARIO":"de 13:00 a 16:00 horas","HORARIO_I":"","HORARIO_V":"","PRECIO":"Ensalada vegetal + agua: 2,85 Euros#Ensalada vegetal + zumo: 3,25 Euros#Ingrediente extra: 0,40 Euros#Vasito de fruta : 1,50 Euros#Ensalada de frutas: 2,85 Euros#"},{"ID_BAR":"1","NOMBRE_BAR":"BAR_2","NOMBRE_BAR_V":"BAR_2","NOMBRE_BAR_I":"BAR_2","LONGITUD":"","LATITUD":"","EMAIL_BAR":"","TELEF":"","TELEF_2":"","WEB":"","FECHA":"27/12/2017","MENU":"Menú del día","PLATO1":"A elegir entre: #- Ensalada del día :s:#- Salmorejo#- Canelones a la boloñesa#- Menestra al natural","PLATO2":"A elegir entre: #- Arroz al horno#- Suquet de cazón :s:#- Burguer BBQ con cebolla caramelizada#- Espinacas a la crema ","OTROS":"Postres a elegir:# - Fruta de temporada # - Yogurt :s:# - Postre casero,# - Tartas variadas ","OBSERVACIONES":"Incluido: Pan, 1/5 de cerveza o 1/4 de agua","HORARIO":" De 13:30 a 16:00","HORARIO_I":"","HORARIO_V":"","PRECIO":"5,00 Euros"},{"ID_BAR":"2","NOMBRE_BAR":"BAR_3","NOMBRE_BAR_V":"BAR_3","NOMBRE_BAR_I":"BAR_3","LONGITUD":"","LATITUD":"","EMAIL_BAR":"","TELEF":"","TELEF_2":"","WEB":"","FECHA":"27/12/2017","MENU":"Menú del día","PLATO1":" A elegir entre: #- Paella valenciana#- Crema de calabacín#- Sopa de marisco#- Raviolis dipepone","PLATO2":" A elegir entre: #- Muslo de pavo en salsa#- Ragut de ternera al vino#- Bacalao a la miel##","OTROS":"Postre","OBSERVACIONES":"El menú incluye bebida, pan y café#","HORARIO":"de 12:45 a 18:00 horas","HORARIO_I":"","HORARIO_V":"","PRECIO":"7,20 Euros"},{"ID_BAR":"2","NOMBRE_BAR":"BAR_3","NOMBRE_BAR_V":"BAR_3","NOMBRE_BAR_I":"BAR_3","LONGITUD":"","LATITUD":"","EMAIL_BAR":"","TELEF":"","TELEF_2":"","WEB":"","FECHA":"27/12/2017","MENU":"Bocatas del día","PLATO1":"Especial del día: #- Pechuga al roquefort#Bocatas del día: #- Magro con tomate y pimiento#- Revuelto de bacon#- Vegetal","PLATO2":"","OTROS":"","OBSERVACIONES":"","HORARIO":"de 9 a 12:30 hotas","HORARIO_I":"","HORARIO_V":"","PRECIO":"Especial del día: 4 Euros (incluye Bebida + aceitunas o cacaos)#Bocatas del día: 2,90 Euros (incluye bebida)"},{"ID_BAR":"2","NOMBRE_BAR":"BAR_3","NOMBRE_BAR_V":"BAR_3","NOMBRE_BAR_I":"BAR_3","LONGITUD":"","LATITUD":"","EMAIL_BAR":"","TELEF":"","TELEF_2":"","WEB":"","FECHA":"27/12/2017","MENU":"Tardeos","PLATO1":"Litro o 2 tercios de cerveza + Bravas: 5 euros#Litro o 2 tercios de cerveza + Ensaladilla Rusa: 5 euros #Litro o 2 tercios de cerveza + Fingers: 5,50 euros#Litro o 2 tercios de cerveza + Rabo o morro: 5,50  euros#","PLATO2":"","OTROS":"","OBSERVACIONES":"","HORARIO":"","HORARIO_I":"","HORARIO_V":"","PRECIO":""},{"ID_BAR":"2","NOMBRE_BAR":"BAR_3","NOMBRE_BAR_V":"BAR_3","NOMBRE_BAR_I":"BAR_3","LONGITUD":"","LATITUD":"","EMAIL_BAR":"","TELEF":"","TELEF_2":"","WEB":"","FECHA":"27/12/2017","MENU":"Menú ensalada","PLATO1":"Ensalada Mediterránea #+#Bebida#+#Postre o café","PLATO2":"","OTROS":"","OBSERVACIONES":"","HORARIO":"","HORARIO_I":"","HORARIO_V":"","PRECIO":"5 euros"}]'

DB_RESTAURANTS = {0: 'BAR_1', 1: 'BAR_2', 2: 'BAR_3'}
DB_MENUS = {0: {0: 'Ensaladas'}, 1: {0: 'Menú del día'},
            2: {0: 'Menú del día', 1: 'Bocatas del día', 2: 'Tardeos', 3: 'Menú ensalada'}}
DB_SUBS = {28679234: {20: [0], 1: [0], 2: [1]}}

THREAD_TIMER_SECONDS = 30
SUBS_WEEKDAY_LIST = range(7)
SUBS_HOUR_INTERVAL = [0, 24]


class MockedExecution(unittest.TestCase):
    saved_reports = {}

    @patch('dagan.database.db_manager.DBManager.report_menu')
    @patch('dagan.database.db_manager.DBManager.unsubscribe')
    @patch('dagan.database.db_manager.DBManager.subscribe')
    @patch('dagan.database.db_manager.DBManager.read_reports')
    @patch('dagan.database.db_manager.DBManager.read_subscriptions')
    @patch('dagan.database.db_manager.DBManager.read_menus')
    @patch('dagan.database.db_manager.DBManager.read_restaurants')
    @patch('dagan.upv.menu_bot.MenuBot.request_info')
    @patch('dagan.upv.menu_bot.MenuBot.request_token')
    def test_change_date(self, request_token, request_info, read_restaurants, read_menus, read_subscriptions,
                         read_reports, subscribe, unsubscribe, report_menu):
        request_token.side_effect = lambda: TOKEN
        request_info.side_effect = lambda: INFO_JSON

        read_restaurants.side_effect = lambda: DB_RESTAURANTS
        read_menus.side_effect = lambda: DB_MENUS
        read_subscriptions.side_effect = lambda: DB_SUBS
        read_reports.side_effect = lambda: self.saved_reports
        subscribe.side_effect = lambda *args, **kwargs: None
        unsubscribe.side_effect = lambda *args, **kwargs: None
        report_menu.side_effect = self.save_report

        public_parameters.THREAD_TIMER_SECONDS = THREAD_TIMER_SECONDS
        public_parameters.SUBS_WEEKDAY_LIST = SUBS_WEEKDAY_LIST
        public_parameters.SUBS_HOUR_INTERVAL = SUBS_HOUR_INTERVAL
        main()

    def save_report(self, chat_id, res_id, menu_id, report_date=None, mode=None):
        if chat_id not in self.saved_reports.keys():
            self.saved_reports[chat_id] = {}
        if res_id not in self.saved_reports[chat_id].keys():
            self.saved_reports[chat_id][res_id] = []
        if menu_id not in self.saved_reports[chat_id][res_id]:
            self.saved_reports[chat_id][res_id].append(menu_id)
        logging.getLogger(__name__).info(str(mode))


if __name__ == '__main__':
    unittest.main()
