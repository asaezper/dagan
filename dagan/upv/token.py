import json
import logging
import time

from dagan.data import public_parameters


class Token:
    """
    Class for store info and business related to the token for the UPV's API
    """
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
        """
        Read the information inside the text and parse it to the internal variables
        :param text: Token info in plain text
        """
        my_dict = json.loads(text)  # Text information is a dictionary in json format
        # Parsing dict to extract info and save ir in the class
        self.access_token = my_dict[Token.ACCESS_TOKEN]
        if Token.EXPIRES_IN in my_dict:
            self.expiration_time = time.time() + my_dict[Token.EXPIRES_IN]
        elif Token.EXPIRATION_TIME in my_dict:
            self.expiration_time = my_dict[Token.EXPIRATION_TIME]
        self.token_type = my_dict[Token.TOKEN_TYPE]

    def recover(self):
        """
        Read the token info from a expected file
        """
        try:
            with open(public_parameters.TOKEN_FILE) as file:
                self.load(file.readline())
        except:
            logging.getLogger(__name__).warning('No saved token file')

    def save(self):
        """
        Save token info into the expected file
        """
        with open(public_parameters.TOKEN_FILE, 'w') as file:
            file.write(json.dumps({Token.ACCESS_TOKEN: self.access_token, Token.TOKEN_TYPE: self.token_type,
                                   Token.EXPIRATION_TIME: self.expiration_time}))

    def is_active(self):
        """
        Checks if there is a token and it has not expired
        :return: True if the instance references a valid token
        """
        return self.access_token is not None and time.time() < self.expiration_time
