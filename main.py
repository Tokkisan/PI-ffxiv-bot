import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')
target_user_id = '142778198088876032'  # Replace with the ID of the desired user
reaction_gif_path = 'path_to_gif.gif'  # Replace with the path to the reaction GIF

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.author.id == target_user_id and message.content.lower() == 'M A N':
        await message.channel.send('M A N')

    if message.author.id == target_user_id and message.content.lower() == 'MAN':
        await message.channel.send('MAN')

    if message.author.id == target_user_id and message.content.lower() == 'https://tenor.com/view/punch-blue-hoodie-beat-up-gif-15435775':
        await message.channel.send('https://tenor.com/view/punch-blue-hoodie-beat-up-gif-15435775')




    await bot.process_commands(message)

bot.run('MTEyNjU5NzIwMjQwNDQ0MjI2NQ.GbikSe.YyKJurezFm_jTNovmgxl7LbB0ACYY6uXtuSToY')
