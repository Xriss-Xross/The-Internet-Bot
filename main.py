
import json
import discord
from discord.ext import commands
from youtubesearchpython import VideosSearch
import youtube_dl
import asyncio
import os

FFMPEG_OPTIONS = {
    "before_options":
    "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}
YDL_OPTIONS = {"format": "bestaudio"}

TOKEN = "ODk4Njc5MjY4Nzg2MTgwMTk2.YWnuSg.E3kwOXGsk92Y8mDqrLWVUTnYsyE"
PREFIX = "~"
LIMIT = 5
QUEUE = []
client = commands.Bot(command_prefix=PREFIX)
client.remove_command('help')

@client.event
async def on_ready():
    print('Bot Online:{0.user}'.format(client))
    await client.change_presence(activity=discord.Activity(
        type=discord.ActivityType.listening, name="everyone"))

client.run(TOKEN)
