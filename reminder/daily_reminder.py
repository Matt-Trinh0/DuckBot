import asyncio
import helpers.time as time_helpers
import helpers.discord as discord_helpers
import datetime as dt
import discord
import random

from economy import Economy

class DailyReminder:
    def __init__(self, bot):
        self.lock = asyncio.Lock()
        self.cd = 0
        self.prev = None
        self.bot = bot
        self.econ = Economy.get_instance(self.bot.remind_server)
        self.capturer = None
        self.reminder_phrases = ['Have a reminder!', 'Don\'t forget!']
        self.remind_msg = 'Congratulations! You\'re the first message of the day.'
        self.remind_attach = 'images/vaporeon.png'

    def set_reminder(self, capturer : discord.User, new_msg, new_attach):
        if capturer == self.capturer:
            self.remind_msg = new_msg
            self.remind_attach = new_attach

    async def remind(self, message):
        # Extract information about the message
        msg_server = message.guild
        msg_channel = message.channel
        msg_user = message.author
        send_time = message.created_at

        # Reminder server info
        remind_server = self.bot.remind_server
        remind_channel = self.bot.remind_channel

        # If this bot was the one who sent the message or the bot receives a DM, then ignore
        if msg_user == self.bot.user or not msg_server or not msg_channel:
            return None

        # Convert the message time from UTC to AZ time
        send_time = time_helpers.convert_tz(send_time, 'UTC', 'America/Phoenix')

        # The earliest time to find the previous reminder is at yesterday 6 am
        yesterday_time = send_time - dt.timedelta(days=1)
        yesterday_time = yesterday_time.replace(hour=6, minute=0, second=0, microsecond=0)
        earliest_prev_time = time_helpers.convert_tz(yesterday_time, 'America/Phoenix', 'UTC')
        earliest_prev_time = earliest_prev_time.replace(tzinfo=None)

        # Get the last reminder this bot sent
        if not self.prev:
            # The last reminder sent by the bot is identified by the message content containing one of the reminder phrases
            last_message_conds = lambda m: m.author == self.bot.user and any(phrase for phrase in self.reminder_phrases if phrase in m.content)

            # Get the last reminder and the capturer of the reminder
            msg_history = msg_channel.history(after=earliest_prev_time, oldest_first=False)
            last_message = None
            prev_msg = None
            async for msg in msg_history:
                if last_message_conds(msg):
                    last_message = msg
                    self.prev = msg
                    self.capturer = prev_msg.author
                    break
                prev_msg = msg
        else:
            last_message = self.prev

        # Check that we haven't already sent a reminder today
        if last_message:
            last_message_time = time_helpers.convert_tz(last_message.created_at, 'UTC', 'America/Phoenix')

            # If we are still on cooldown then send back
            if self.cd and (send_time - self.cd) < last_message_time:
                return None

            # Last reminder was not sent today (or later) 
            if last_message_time.date() >= send_time.date() or send_time.hour < 6:
                return None

        # If the server and channel the message came from are not the server and channel we want to remind
        # then ignore
        if msg_server.name != remind_server or msg_channel.name != remind_channel:
            return None

        # Apply one of the reminder phrases to the reminder message (append if there is an attachment, pre-append if not)
        curr_reminder_phrase = random.sample(self.reminder_phrases, 1)[0]
        reminder_parts = [self.remind_msg, curr_reminder_phrase] if self.remind_attach else [curr_reminder_phrase, self.remind_msg]
        full_reminder = ' '.join(reminder_parts)

        # Send the daily reminder if all these checks are passed and set the previous daily reminder to this one
        self.prev = await discord_helpers.send_msg_to(msg_server, msg_channel, full_reminder, self.remind_attach)
        self.capturer = msg_user

        # Add points to the user that triggered this then save it
        self.econ.add(msg_user.name, 10)
        self.econ.save()

        # Set the cooldown for the daily reminder until tomorrow at 6 am
        tomorrow_time = send_time + dt.timedelta(days=1)
        self.cd = tomorrow_time.replace(hour=6, minute=0, second=0, microsecond=0) - send_time
