import asyncio
import yaml

from random import sample

from .constants import REMIND_FILE

class Reminder:
    def __init__(self, bot, tz = 'America/Phoenix'):
        self.lock = asyncio.Lock()
        self.cd = 0
        self.prev = None
        self.bot = bot
        self.remind_msg = RemindMessage()
        self.tz = tz

        # Parse the server name before creating or accessing the file for it
        parsed_server_name = ''.join(char for char in self.bot.remind_server if char.isalnum())
        self.remind_file = REMIND_FILE.replace('SERVER', parsed_server_name)

        # Load reminder config file
        with open(self.remind_file) as f:
            remind_info = yaml.safe_load(f)

        self.remind_msg = RemindMessage(remind_info, 'vaporeon')

class RemindMessage:
    def __init__(self, remind_cfg, name):
        self.__name = name
        self.__msg = remind_cfg[self.__name]['msg']
        self.__attach = remind_cfg[self.__name]['attach']
        self.__phrases = ['Have a reminder!', 'Don\'t forget!']

    @property
    def msg(self):
        remind_msg = ''
        if isinstance(self.__msg, str):
            remind_msg = self.__msg
        elif isinstance(self.__msg, list):
            remind_msg = sample(self.__msg, 1)[0]
        else:
            return None

        # Apply one of the reminder phrases to the reminder message (append if there is an attachment, pre-append if not)
        curr_reminder_phrase = sample(self.__phrases, 1)[0]
        reminder_parts = [remind_msg, curr_reminder_phrase] if self.__attach else [curr_reminder_phrase, remind_msg]
        full_reminder = ' '.join(reminder_parts)

        return full_reminder

    @property
    def attach(self):
        if isinstance(self.__attach, str):
            return self.__attach
        elif isinstance(self.__attach, list):
            return sample(self.__attach, 1)[0]
        else:
            return None

    