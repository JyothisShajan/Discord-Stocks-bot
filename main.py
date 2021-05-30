import os
import discord
from quotes import random_quotes
from discord.ext import commands
import yfinance as yf
import seaborn as sns
import matplotlib.pyplot as plt
import json 


sns.set(style="whitegrid")
sns.set_palette("deep", 10)
sns.set_context("paper", font_scale = .8)

async def determine_prefix(bot, message):
  with open("prefixes.json", "r") as f:
    prefixes = json.load(f)

  return prefixes[str(message.guild.id)]


bot = commands.Bot(command_prefix = determine_prefix)
bot.remove_command('help')

watchlist={}

@bot.event
async def on_ready():
  print('Logged in as')
  print(bot.user.name)

@bot.event
async def on_guild_join(guild):
  with open("prefixes.json", "r") as f:
    prefixes = json.load(f)

  prefixes[str(guild.id)] = "$"

  with open("prefixes.json", 'w') as f:
    json.dump(prefixes, f, indent = 4)

@bot.event
async def on_guild_remove(guild):
  with open("prefixes.json", "r") as f:
    prefixes = json.load(f)

  prefixes.pop[str(guild.id)] = "$"

  with open("prefixes.json", 'w') as f:
    json.dump(prefixes, f, indent = 4)

@bot.command(name = "changeprefix")
async def changeprefix(ctx, prefix):
  with open("prefixes.json", "r") as f:
    prefixes = json.load(f)

  prefixes[str(ctx.guild.id)] = prefix

  with open("prefixes.json", 'w') as f:
    json.dump(prefixes, f, indent = 4)

  await ctx.send("Prefix changed to {}".format(prefix))

@bot.command(name = "graph") 
async def gr(ctx, company, period):
  plt.clf()
  newtime = yf.download(company, period=period, interval = "1d", group_by = 'ticker', auto_adjust = True)
  for i in ['Open', 'High', 'Close', 'Low']: 
    newtime[i]  =  newtime[i].astype('float64')

  fig = sns.lineplot(x = "Date", y = "Close", data = newtime).set_title("{} ({})".format(company.upper(), period))
  fig.figure.autofmt_xdate()
  fig.figure.savefig("plot.png")
  file=discord.File('plot.png')
  embed = discord.Embed(title="The Chart is available", description="[Click here](https://in.tradingview.com/chart/?symbol={})".format(company.upper()), color=0x22f0b9)

  await ctx.send(file=file, embed=embed)

@bot.command(name = "addwatch") 
async def addwatch(ctx, *, company):
  company = company.upper()
  id = ctx.author.id
  desc = ""
  if id in watchlist:
    if company in watchlist[id]:
      desc = "{} is already added to {}'s watchlist".format(company, ctx.author.name)
    else:
      watchlist[id].append(company)
      desc = "{} added to {}'s watchlist".format(company, ctx.author.name)
  else:
    watchlist[id] = [company]
    desc = "{} added to {}'s watchlist".format(company, ctx.author.name)
  embed = discord.Embed(title="Watchlist", description=desc, color=0x99ecff)
  await ctx.send(embed=embed)


@bot.command(name = "removewatch") 
async def removewatch(ctx, *, company):
  company = company.upper()
  id = ctx.author.id
  desc = ""
  if id in watchlist:
    if company in watchlist[id]:
      watchlist[id].remove(company)
      desc = "{} removed to {}'s watchlist".format(company, ctx.author.name)
    else:
      desc = "{} is not present in {}'s watchlist".format(company, ctx.author.name)
  else:
    desc = "{}'s Wishlist is empty".format(ctx.author.name)
  embed = discord.Embed(title="Watchlist", description=desc, color=0x99ecff)
  await ctx.send(embed=embed)

@bot.command(name = "showwatch") 
async def showwatch(ctx):
  id = ctx.author.id
  if id in watchlist:
    embed = discord.Embed(title="Watchlist of {}".format(ctx.author.name), description="", color=0x99ecff)
    for i in watchlist[id]:
      ticker = yf.Ticker(i)
      stock_det = ticker.info
      embed.add_field(name="{}".format(i), value=("$" + str(stock_det["bid"])))
  else:
    embed = discord.Embed(title="Watchlist of {}".format(ctx.author.name), description="{}'s Wishlist is empty".format(ctx.author.name), color=0x99ecff)
  await ctx.send(embed=embed)

@bot.command(name = "price") 
async def price(ctx, *, company):
  ticker = yf.Ticker(company)
  stock_det = ticker.info
  embed = discord.Embed(title="Stock info", description="", color=0x22f0b9)
  embed.set_author(name=stock_det["shortName"] , icon_url=stock_det["logo_url"])
  embed.set_thumbnail(url=stock_det["logo_url"])
  embed.add_field(name="Bid: ", value=("$" + str(stock_det["bid"])) , inline=False)
  embed.add_field(name="Market Open: ", value=("$" + str(stock_det["regularMarketOpen"])), inline=False)
  embed.add_field(name="Market Day High: ", value=("$" + str(stock_det["regularMarketDayHigh"])), inline=True)
  embed.add_field(name="Market Day Low: ", value=("$" + str(stock_det["regularMarketDayLow"])), inline=True)
  embed.add_field(name="Market Capital: ", value=("$"+ str(stock_det["marketCap"])), inline=False)
  embed.add_field(name="52 Week high: ", value=("$" + str(stock_det["fiftyTwoWeekHigh"])), inline=True)
  embed.add_field(name="52 Week low: ", value=("$" + str(stock_det["fiftyTwoWeekLow"])), inline=True)
  embed.set_footer(text=random_quotes())
  await ctx.send(embed=embed)

@bot.command(name = "info") 
async def info(ctx, *, company):
  ticker = yf.Ticker(company)
  yf.download(company)
  stock_det = ticker.info
  embed = discord.Embed(title=stock_det["shortName"],url=stock_det["website"], description=stock_det["longBusinessSummary"], color=0x99ecff)
  embed.set_thumbnail(url=stock_det["logo_url"])
  embed.add_field(name="Market Sector: ", value= stock_det["industry"], inline=True)
  embed.add_field(name="Enterprise Value: ", value=("$" + str(stock_det["enterpriseValue"])), inline=True)
  embed.set_footer(text=random_quotes())
  await ctx.send(embed=embed)
 
@bot.command(name = "help") 
async def help(ctx):
  embed = discord.Embed(title="Help!",description="How to use commands", color=0xff4202)
  embed.add_field(name="$info <ticker> : ", value= "Gives company info", inline=False)
  embed.add_field(name="Stock Market Analysis - ", value= "_", inline=False)
  embed.add_field(name="$price <ticker> : ", value="Gives current stock market rates", inline=True)
  embed.add_field(name="$graph <ticker> : ", value="Get graph for stock market analysis over a specific period of time. ", inline=True)
  embed.add_field(name="$compare ticker : ", value="Get a comparison graph to compare multiple companies", inline=True) 
  embed.set_footer(text=random_quotes())
  embed.add_field(name="The Watchlist Commands - ", value= "_", inline=False)
  embed.add_field(name="$addwatch <ticker>: ", value= "Add company to WatchList", inline=True)
  embed.add_field(name="$removewatch <ticker> : ", value= "Remove  company from WatchList", inline=True)
  embed.add_field(name="$showwatch  : ", value= "Show Watchlist", inline=True)
  await ctx.send(embed=embed)
 
@bot.command(name = "compare")
async def compare(ctx, period, *company):
  plt.clf()
  for i in company:
    newtime = yf.download(i, period=period, interval = "1d", group_by = 'ticker', auto_adjust = True)
    for j in ['Open', 'High', 'Close', 'Low']: 
      newtime[i]  =  newtime[j].astype('float64')
    fig = sns.lineplot(x = "Date", y = "Close", data = newtime).set_title("Comaprison of {} for ({})".format(', '.join(company).upper(), period))
    
  fig.figure.autofmt_xdate()
  plt.legend(labels=company)
  fig.figure.savefig("plot.png")
  
  await ctx.send(file=discord.File('plot.png'))


my_secret = os.environ['TOKEN']
bot.run(my_secret)
