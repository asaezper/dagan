import json
import logging
import time

from dagan.internal_data import upv_parameters, dagan_parameters


class UPVToken:
    ACCESS_TOKEN = 'access_token'
    EXPIRES_IN = 'expires_in'
    EXPIRATION_TIME = 'expiration_time'
    TOKEN_TYPE = 'token_type'

    def __init__(self):
        self.access_token = None
        self.expiration_time = None
        self.token_type = None
        self.recover()

    def load(self, text):
        my_dict = json.loads(text)
        self.access_token = my_dict[UPVToken.ACCESS_TOKEN]
        if UPVToken.EXPIRES_IN in my_dict:
            self.expiration_time = time.time() + my_dict[UPVToken.EXPIRES_IN]
        elif UPVToken.EXPIRATION_TIME in my_dict:
            self.expiration_time = my_dict[UPVToken.EXPIRATION_TIME]
        self.token_type = my_dict[UPVToken.TOKEN_TYPE]

    def recover(self):
        try:
            with open(dagan_parameters.TOKEN_FILE) as file:
                self.load(file.readline())
        except:
            logging.getLogger(__name__).warning('No saved token file')

    def save(self):
        with open(dagan_parameters.TOKEN_FILE, 'w') as file:
            file.write(json.dumps({UPVToken.ACCESS_TOKEN: self.access_token, UPVToken.TOKEN_TYPE: self.token_type,
                                   UPVToken.EXPIRATION_TIME: self.expiration_time}))

    def is_active(self):
        return self.access_token is not None and time.time() < self.expiration_time
