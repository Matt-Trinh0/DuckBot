import asyncio
import helpers
import datetime as dt

from economy import Economy

class DailyReminder:
    def __init__(self, bot):
        self.bot = bot
        self.econ = Economy(self.bot.remind_server)
        self.next_send_time = 0

    async def remind(self, message):
        # Extract information about the message
        msg_server = message.guild
        msg_channel = message.channel
        msg_user = message.author
        send_time = message.created_at

        # Reminder server info
        remind_server = self.bot.remind_server
        remind_channel = self.bot.remind_channel
        remind_msg = 'Congratulations! You\'re the first message of the day. Have a reminder! :)'

        # If bot gets restarted then we can try and prevent duplicate messages in one day
        if self.next_send_time == 0:
            # The earliest time to find the previous reminder is at yesterday 6 am
            yesterday_time = send_time - dt.timedelta(days=1)
            yesterday_time = yesterday_time.replace(hour=6, minute=0, second=0, microsecond=0)
            earliest_prev_time = helpers.convert_tz(yesterday_time, 'America/Phoenix', 'UTC')
            earliest_prev_time = earliest_prev_time.replace(tzinfo=None)

            # Get the last message this bot sent
            last_message = await msg_channel.history(after=earliest_prev_time, oldest_first=False).get(author=self.bot.user, content=remind_msg)
            if last_message:
                # Set the cooldown for the daily reminder until tomorrow at 6 am
                if last_message.created_at.hour < 6:
                    self.next_send_time = last_message.created_at.replace(hour=6, minute=0, second=0, microsecond=0)
                else:
                    tomorrow_time = last_message.created_at + dt.timedelta(days=1)
                    self.next_send_time = tomorrow_time.replace(hour=6, minute=0, second=0, microsecond=0)

        # If this bot was the one who sent the message or the bot receives a DM, then ignore
        if msg_user == self.bot.user or not msg_server or not msg_channel:
            return None

        # Convert the message time from UTC to AZ time
        send_time = helpers.convert_tz(send_time, 'UTC', 'America/Phoenix')

        # check if it is time to send another reminder
        if send_time < self.next_send_time:
            return None

        # If the server and channel the message came from are not the server and channel we want to remind
        # then ignore
        if msg_server.name != remind_server or msg_channel.name != remind_channel:
            return None

        # Send the daily reminder if all these checks are passed and record that we sent it
        await helpers.send_msg_to(msg_server, msg_channel, remind_msg, 'images/vaporeon.png')

        # Update the leaderboard with the score then save it
        self.econ.add(msg_user.name, 10)
        self.econ.save()

        # Set the cooldown for the daily reminder until tomorrow at 6 am
        if send_time.hour < 6:
            self.next_send_time = send_time.replace(hour=6, minute=0, second=0, microsecond=0)
        else:
            tomorrow_time = send_time + dt.timedelta(days=1)
            self.next_send_time = tomorrow_time.replace(hour=6, minute=0, second=0, microsecond=0)
