import discord
import discord.ext.commands as disc_cmds
import os
import sys
import helpers
import discord
import duck_api
import io
import aiohttp

from economy import Economy

class CommandManager(disc_cmds.Cog, name='CommandManager'):
    def __init__(self, bot):
        self.bot = bot

    @disc_cmds.command(name='say')
    async def say(self, ctx, server : discord.Guild, channel : discord.TextChannel, msg):
        owner = await self.bot.is_owner(ctx.author)
        if owner:
            await helpers.send_msg_to(server, channel, msg, None)
        else:
            print('You are not the owner')

    @disc_cmds.command(name='leaderboard')
    async def reminder_leaderboard(self, ctx, limit: int = 10):
        # TODO Implement pagination
        # Get the rankings from the reminder leaderboard
        economy = Economy(ctx.guild.name)
        rankings = [rank for rank in economy.get_rankings(limit)]

        # Create the leaderboard message and send
        name_string = '\n'.join([rank[1] for rank in rankings])
        point_string = '\n'.join([str(rank[2]) for rank in rankings])
        rank_string = '\n'.join([str(rank[0]) for rank in rankings])

        leaderboard_embed = discord.Embed()
        leaderboard_embed.title = f'Economy Rankings for {ctx.guild.name}'
        leaderboard_embed.add_field(name='Rank', value=rank_string if rank_string else 'N/A')
        leaderboard_embed.add_field(name='Names', value=name_string if name_string else 'N/A')
        leaderboard_embed.add_field(name='Points', value=point_string if point_string else 'N/A')
        await ctx.send(embed=leaderboard_embed)

    @disc_cmds.command(name='duckfact')
    async def duck_fact(self, ctx):
        duck = duck_api.DuckFact()
        image = duck.getImage()
        fact = duck.getFact()

        async with aiohttp.ClientSession() as session:
            async with session.get(image) as resp:
                if resp.status != 200:
                    return await ctx.send('Could not download file...')
                data = io.BytesIO(await resp.read())
                await ctx.send(file=discord.File(data, 'duck.png'), content=fact)



    # TODO This command should be used for the bot to update itself
    # ! DEPRECATED for now
    # @disc_cmds.command(name='update')
    # async def update(self, ctx):
    #     print(sys.executable)
    #     print(sys.argv)
    #     await ctx.send('you called?')
