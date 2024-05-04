import discord
from discord.ext import commands
from datetime import datetime, timedelta
import math
import pytz
from pytz import timezone
import time
import random
import requests
from time import strftime, localtime
import asyncio
import logging
import aiohttp
import pyxivapi  
from pyxivapi.models import Filter, Sort
import re


intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

bot.remove_command('help')
@bot.command(name = 'help')
async def help(ctx, function_name = None):
  if function_name is None:
    await ctx.send("List of commands:\n :grey_question: help + function_name\n :ping_pong: ping\n :clock12: timezones\n :fishing_pole_and_fish: fishing\n :stopwatch: timestamp\n :punch: man\n :cloud: weather\n :scroll: frecipe")
    
  elif function_name.lower() == 'ping':
    await ctx.send("Ping: tests latency of bot")

  elif function_name.lower() == 'timezones':
    await ctx.send("Timezones: shows the timezones of UTC, LA, Vietnam, NY, and Australia currently")

  elif function_name.lower() == 'fishing':
    await ctx.send("Fishing: shows ocean fishing schedule for current and next route with baits included")
  elif function_name.lower() == 'timestamp':
    await ctx.send("Timestamp: input any number of hours as an integer to output a relative timestamp")
  elif function_name.lower() == 'man':
    await ctx.send("Man: outputs gifs that sam would use :)")
  elif function_name.lower() == 'weather':
    await ctx.send("Weather: input any city to get the weather temp in F/C and weather description")
  elif function_name.lower() == 'frecipe':
    await ctx.send("frecipe: input any craftable recipe and it will output description and some of its effects")
  else:
    await ctx.send(f'{function_name} is not a valid command')




@bot.command(name='ping')
async def ping(ctx):
  await ctx.send('pong')


@bot.command(name='timezones')
async def timezones(ctx):
  now_utc = datetime.now(timezone('UTC'))
  LA = now_utc.astimezone(timezone('America/Los_Angeles'))
  Viet = now_utc.astimezone(timezone('Asia/Ho_Chi_Minh'))
  NY = now_utc.astimezone(timezone('America/New_York'))
  Aus = now_utc.astimezone(timezone('Australia/Sydney'))

  message = (f':clock12: UTC: {now_utc.strftime("%I:%M:%S %p")}\n'
             f':flag_us: LA:    {LA.strftime("%I:%M:%S %p")}\n'
             f':flag_vn: Viet:  {Viet.strftime("%I:%M:%S %p")}\n'
             f':flag_us: NY:    {NY.strftime("%I:%M:%S %p")}\n'
             f':flag_au: Aus:   {Aus.strftime("%I:%M:%S %p")}\n')
  await ctx.send(message)

PATTERN = [
    'BD', 'TD', 'MD', 'RD', 'BS', 'TS', 'MS', 'RS', 'BN', 'TN', 'MN', 'RN',
    'TD', 'MD', 'RD', 'BS', 'TS', 'MS', 'RS', 'BN', 'TN', 'MN', 'RN', 'BD',
    'MD', 'RD', 'BS', 'TS', 'MS', 'RS', 'BN', 'TN', 'MN', 'RN', 'BD', 'TD',
    'RD', 'BS', 'TS', 'MS', 'RS', 'BN', 'TN', 'MN', 'RN', 'BD', 'TD', 'MD',
    'BS', 'TS', 'MS', 'RS', 'BN', 'TN', 'MN', 'RN', 'BD', 'TD', 'MD', 'RD',
    'TS', 'MS', 'RS', 'BN', 'TN', 'MN', 'RN', 'BD', 'TD', 'MD', 'RD', 'BS',
    'MS', 'RS', 'BN', 'TN', 'MN', 'RN', 'BD', 'TD', 'MD', 'RD', 'BS', 'TS',
    'RS', 'BN', 'TN', 'MN', 'RN', 'BD', 'TD', 'MD', 'RD', 'BS', 'TS', 'MS',
    'BN', 'TN', 'MN', 'RN', 'BD', 'TD', 'MD', 'RD', 'BS', 'TS', 'MS', 'RS',
    'TN', 'MN', 'RN', 'BD', 'TD', 'MD', 'RD', 'BS', 'TS', 'MS', 'RS', 'BN',
    'MN', 'RN', 'BD', 'TD', 'MD', 'RD', 'BS', 'TS', 'MS', 'RS', 'BN', 'TN',
    'RN', 'BD', 'TD', 'MD', 'RD', 'BS', 'TS', 'MS', 'RS', 'BN', 'TN', 'MN'
]

TWO_HOURS = 2 * 60 * 60 * 1000
PST_TIMEZONE = pytz.timezone('America/Los_Angeles')  # Pacific Standard Time

def get_route(date):
  pst_date = date.astimezone(PST_TIMEZONE)
  voyage_number = math.floor((pst_date.timestamp() * 1000 / TWO_HOURS))
  route = PATTERN[(voyage_number - 1) % len(PATTERN)]
  return route

def get_route_next(date):
  pst_date = date.astimezone(PST_TIMEZONE)
  voyage_number = math.floor((pst_date.timestamp() * 1000 / TWO_HOURS))
  nroute = PATTERN[(voyage_number) % len(PATTERN)] 
  return nroute
  

def get_time_description(route):
  if 'D' in route:
    return 'Day'
  elif 'S' in route:
    return 'Sunset'
  elif 'N' in route:
    return 'Night'
bait = ''
def get_bait(route):
  if 'B' in route:
    return 'Rag, Rag, Krill'
  elif 'T' in route:
    return 'Rag, Plump, Plump'
  elif 'M' in route:
    return 'Krill, Krill, Rag'
  elif 'R' in route:
    return 'Krill, Krill, Plump'

def get_route_description(route):
  if 'B' in route:
    return 'BloodBrine Sea'
  elif 'T' in route:
    return 'Rothlyt Sound'
  elif 'M' in route:
    return 'Northern Strait of Merlthor'
  elif 'R' in route:
    return 'Rhotano Sea'

@bot.command()
async def fishing(ctx):
  now_utc = datetime.now(timezone('UTC'))
  current_route = get_route(now_utc)
  
  next_route = get_route_next(now_utc)

  c_time = get_time_description(current_route)
  c_route = get_route_description(current_route)
  c_bait = get_bait(current_route)

  n_time = get_time_description(next_route)
  n_route = get_route_description(next_route)
  n_bait = get_bait(next_route)

  await ctx.send(f"**The current route is: {c_route} : {c_time}**")
  await ctx.send(f"Bait is : {c_bait}")
  await ctx.send(f"**The route for the next trip is: {n_route} : {n_time}**")
  await ctx.send(f"Bait is : {n_bait}")
  await ctx.send("For more info please visit https://ffxiv.pf-n.co/ocean-fishing")

@bot.command(name = 'timestamp')
async def timestamp(ctx, hours: int):
  try:
    c_time = int(time.time())
    timestamp = c_time + (hours * 3600)
    t_string = f'<t:{timestamp}:R>'
    await ctx.send(t_string)
    await ctx.send(f'```<t:{timestamp}:R>```')
  
  except ValueError:
    await ctx.send("Not valid integer")

@bot.command(name = 'man')
async def man(ctx):
  r_num = random.randint(1,5)
  
  if r_num == 1:
    await ctx.send("https://tenor.com/view/punches-punching-fighting-angry-hold-me-back-gif-14170843")
  elif r_num == 2:
    await ctx.send("https://tenor.com/view/meme-memes-memes2022funny-meme-face-punch-gif-25436787")
  elif r_num == 3:
    await ctx.send("https://tenor.com/view/waste-of-time-garbage-truck-temper-man-trash-gif-12177562")
  elif r_num == 4:
    await ctx.send("https://tenor.com/view/waste-of-time-garbage-truck-temper-man-trash-gif-12177562")
  elif r_num == 5:
    await ctx.send("https://tenor.com/view/cat-i-am-on-the-brink-meme-white-text-gif-26506151")


api_key = ""
base_url = "http://api.openweathermap.org/data/2.5/weather?"

@bot.command(name='weather')
async def weather(ctx, *, city_name):
  complete_url = base_url + "appid=" + api_key + "&q=" + city_name
  response = requests.get(complete_url)
  x = response.json()

  if x["cod"] != "404":
    y = x["main"]
    current_temperature = y["temp"]
    f_temp = round(((9/5) * (current_temperature - 273.15) + 32), 2)
    c_temp = round((current_temperature - 273.15), 2)

    z = x["weather"]
    weather_description = z[0]["description"]
    result = (
      f'Temperature = {str(f_temp)} F / {str(c_temp)} C\n'
      f'Description = {str(weather_description)}'
    )
    await ctx.send(result)
  else:
    await ctx.send("city not found")




ffxiv_api_key = ""
private_key = "https://xivapi.com/item/1675?private_key="
async def fetch_example_results(ctx, recipe_name, mult):
  client = pyxivapi.XIVAPIClient(ffxiv_api_key)

  # Search for a recipe
  recipe = await client.index_search(
      name = recipe_name,
      indexes = ["Recipe"],
      columns=["ID", "Name", "Icon", "ItemResult.Description",
         'ItemIngredient0.Name', 'AmountIngredient0',
         'ItemIngredient1.Name', 'AmountIngredient1',
         'ItemIngredient2.Name', 'AmountIngredient2',
         'ItemIngredient3.Name', 'AmountIngredient3',
         'ItemIngredient4.Name', 'AmountIngredient4',
         'ItemIngredient5.Name', 'AmountIngredient5',
         'ItemIngredient6.Name', 'AmountIngredient6',
         'ItemIngredient7.Name', 'AmountIngredient7',
         'ItemIngredient8.Name', 'AmountIngredient8',
         'ItemIngredient9.Name', 'AmountIngredient9',
         'AmountResult', 'ClassJob.Name']
    ) 


  # Print information about the recipe
  for result in recipe['Results']:
      r_name = result['Name']
      Classjob = result['ClassJob']['Name']
      item_description = result['ItemResult']['Description']
      I0 = result['ItemIngredient0']['Name']
      I1 = result['ItemIngredient1']['Name']
      I2 = result['ItemIngredient2']['Name']
      I3 = result['ItemIngredient3']['Name']
      I4 = result['ItemIngredient4']['Name']
      I5 = result['ItemIngredient5']['Name']
      I6 = result['ItemIngredient6']['Name']
      I7 = result['ItemIngredient7']['Name']
      I8 = result['ItemIngredient8']['Name']
      I9 = result['ItemIngredient9']['Name']
  
      Q0 = result['AmountIngredient0'] * mult
      Q1 = result['AmountIngredient1'] * mult
      Q2 = result['AmountIngredient2'] * mult
      Q3 = result['AmountIngredient3'] * mult
      Q4 = result['AmountIngredient4'] * mult
      Q5 = result['AmountIngredient5'] * mult
      Q6 = result['AmountIngredient6'] * mult
      Q7 = result['AmountIngredient7'] * mult
      Q8 = result['AmountIngredient8'] * mult
      Q9 = result['AmountIngredient9'] * mult

      crafted_amount = result['AmountResult']
      
      #use https://regexr.com/ 
      fix1 = re.sub(r'F[0-9]{1,5}|<[^>]*>|01|\s{2,}', '',item_description)
      fix2 = re.sub(r'EXP', '\nEXP', fix1)
      fix3 = re.sub(r'Duration: 30m', 'Duration: 30m\n', fix2)
      fixed_description = fix3
    
      if not str(fixed_description):
        fixed_description = "No description"


      await ctx.send(f"**Recipe Name:** {r_name}")
      await ctx.send(f"**Class:** {Classjob}")
      await ctx.send(f"**Amount Produced Per Craft:** {crafted_amount}")
      await ctx.send(f"**Item Description:** *{fixed_description}*")

      f_string = []
      if I0 is not None and Q0 is not None:
        f_string.append(f'{I0:25} : {Q0}')
      if I1 is not None and Q1 is not None:
        f_string.append(f'{I1:25} : {Q1}')
      if I2 is not None and Q2 is not None:
        f_string.append(f'{I2:25} : {Q2}')
      if I3 is not None and Q3 is not None:
        f_string.append(f'{I3:25} : {Q3}')
      if I4 is not None and Q4 is not None:
        f_string.append(f'{I4:25} : {Q4}')
      if I5 is not None and Q5 is not None:
        f_string.append(f'{I5:25} : {Q5}')
      if I6 is not None and Q6 is not None:
        f_string.append(f'{I6:25} : {Q6}')
      if I7 is not None and Q7 is not None:
        f_string.append(f'{I7:25} : {Q7}')
      if I8 is not None and Q8 is not None:
        f_string.append(f'{I8:25} : {Q8}')
      if I9 is not None and Q9 is not None:
        f_string.append(f'{I9:25} : {Q9}')

    
      f_string.append("----------------------------------------")
      total_crafted = crafted_amount * mult
      f_string.append(f'{"Total crafted":25} : {total_crafted}')
        
      final_list = "\n".join(f_string)
      await ctx.send(f'```\n{final_list}\n```')

  
  await client.session.close()

@bot.command(name='frecipe')
async def xiv_recipe(ctx, mult, *,  recipe_name):
  await ctx.send("Searching for XIV recipe...")
  await fetch_example_results(ctx, recipe_name, int(mult))


@bot.command(name = 'housing')
async def lottery(ctx, world, district):
    url = 'https://paissadb.zhu.codes/worlds'
    headers = {'accept': 'application/json'}
    #mist: district=339
    #lavander beds: district=340
    #Goblet: district=341
    #shirogane: district=641
    #empyreum: district= 979
    if district.lower() == "mist":
      district_num = 339
    elif district.lower() == "lavander":
      district_num = 340
    elif district.lower() == "goblet":
      district_num = 341
    elif district.lower() == "shirogane":
      district_num = 641
    elif district.lower() == "empyreum":
      district_num = 979
    

    response = requests.get(url, headers=headers)
    data = response.json()
  

    for values in data:
        if str(values['name'].lower()) == world.lower():
            world_url = f'{url}/{values["id"]}/{district_num}'

    lottery = requests.get(world_url, headers=headers)
    lottery_data = lottery.json()

    output = []
    output.append("ward  plot  size   price     entries  last_updated_time\n")

    for values in lottery_data["open_plots"]:
        if values['lotto_phase'] == 1 and values['lotto_entries'] <= 20:
            update_time = strftime('%I:%M:%S', localtime(values['last_updated_time']))
            if values['size'] == 0:
                size = "sml"
            elif values['size'] == 1:
                size = "med"
            elif values['size'] == 2:
                size = "lrg"
            output.append(f"{values['ward_number']:<5} {values['plot_number']:<3}   {size:<7}{values['price']:<8}  {values['lotto_entries']:<7}  {update_time} hours ago\n")

    await ctx.send(f'```{"".join(output)}```')

token = ''
bot.run(token)

