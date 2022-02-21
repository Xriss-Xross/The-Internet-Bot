
import json
import discord
from discord.ext import commands
from youtubesearchpython import VideosSearch
from dotenv import load_dotenv
import youtube_dl
import asyncio
import os

FFMPEG_OPTIONS = {
    "before_options":
    "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}
YDL_OPTIONS = {"format": "bestaudio"}

load_dotenv()
TOKEN = os.getenv("TOKEN")
PREFIX = os.getenv("PREFIX")
LIMIT = 5
QUEUE = []
client = commands.Bot(command_prefix=PREFIX)
client.remove_command('help')

@client.event
async def on_ready():
    print('Bot Online:{0.user}'.format(client))
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="everyone"))


async def checkQueue(ctx):
    if QUEUE != []:
        QUEUE.pop(0)
    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        voice_client = ctx.voice_client
        info = ydl.extract_info(QUEUE[0][1], download=False)
        url2 = info["formats"][0]["url"]
        source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
        voice_client.play(source, after=lambda x=None: asyncio.run(checkQueue(ctx)))


@client.command(name="ping")
async def ping(ctx):
    await ctx.send(f"Pong! Latency: {round(client.latency * 1000)} ms")


@client.command(aliases=["HELP", "h", "H"])
async def help(ctx):
    await ctx.channel.send("No")


@client.command(aliases=["dc", "fuckoff", "FUCKOFF", "DC", "DISCONNECT"])
async def disconnect(ctx):
    if (ctx.voice_client):
        await ctx.voice_client.disconnect()
        await ctx.send("Bye! :wave:")
    else:
        await ctx.send("I'm not currently in a voice channel")


@client.command(aliases=["p", "P", "PLAY"])
async def play(ctx, *args):
    if ctx.author is None:
        await ctx.send("You aren't in a voice channel")
    channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await channel.connect()
    else:
        await ctx.voice_client.move_to(channel)

    if args[0].startswith("https://www.youtube.com/watch?v="):
        searchQuery = VideosSearch(args[0], limit=1)
        songName = searchQuery.result()["result"][0]["title"]
        songLink = "https://www.youtube.com/watch?v=" + searchQuery.result()["result"][0]["id"]
        voice_client = ctx.voice_client
        QUEUE.append([songName, args[0]])
        if ctx.voice_client.is_playing():
            pass
        else:
            with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(QUEUE[0][1], download=False)
                url2 = info["formats"][0]["url"]
                source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
                voice_client.play(source, after=lambda x=None: asyncio.run(checkQueue(ctx)))
                embed = discord.Embed(color=0xff0000)
                embed.add_field(name=f"Added to queue: {songName}", value=songLink, inline=False)
                await ctx.send(embed=embed)

    else:
        searchQueryArgs = " ".join(args)
        searchQuery = VideosSearch(searchQueryArgs, limit=1)
        songName = searchQuery.result()["result"][0]["title"]
        songLink = "https://www.youtube.com/watch?v=" + searchQuery.result()["result"][0]["id"]
        voice_client = ctx.voice_client
        QUEUE.append([songName, songLink])
        if ctx.voice_client.is_playing():
            pass
        else:
            with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(QUEUE[0][1], download=False)
                url2 = info["formats"][0]["url"]
                source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
                voice_client.play(source, after=lambda x=None: asyncio.run(checkQueue(ctx)))
                embed = discord.Embed(color=0xff0000)
                embed.add_field(name=f"Added to queue: {songName}", value=songLink, inline=False)
                await ctx.send(embed=embed)


@client.command(aliases=["q", "Q", "QUEUE"])
async def queue(ctx):
    if len(QUEUE) == 0:
        await ctx.send("It doesn't look like there is a queue right now. Try **~play** to add some beats to the queue :headphones:")
    else:
        for i in range(len(QUEUE)):
            embed = discord.Embed(color=0xff0000)
            embed.add_field(name=QUEUE[i][0], value=QUEUE[i][1], inline=False)    
    await ctx.send(embed=embed)


@client.command(aliases=["cq", "CQ", "CLEARQUEUE"])
async def clearqueue(ctx):
    for i in QUEUE:
        QUEUE.pop()


@client.command(aliases=["fs", "FS", "s", "S", "SKIP"])
async def skip(ctx):
    QUEUE.pop(0)
    voice_client = ctx.voice_client
    if len(QUEUE) != 0:
        ctx.voice_client.stop()
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(QUEUE[0][1], download=False)
            url2 = info["formats"][0]["url"]
            source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
            voice_client.play(source)
    else:
        voice_client = ctx.voice_client
        voice_client.stop()


@client.command(aliases=["PAUSE", "pu", "PU"])
async def pause(ctx):
    voice_client = ctx.voice_client
    if voice_client.is_playing():
        voice_client.pause()
    else:
        await ctx.send(
            "There is currently no audio playing in the voice channel")


@client.command(name="resume")
async def resume(ctx):
    voice_client = ctx.voice_client
    if voice_client.is_paused():
        voice_client.resume()
    else:
        await ctx.send("There is currently no audio paused")


@client.command(aliases=["summon", "SUMMON", "j", "J", "JOIN"])
async def join(ctx):
    if ctx.author.voice is None:
        await ctx.send("You aren't in a voice channel")
    channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await channel.connect()
    else:
        await ctx.voice_client.move_to(channel)
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(QUEUE[0][1], download=False)
            url2 = info["formats"][0]["url"]
            source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
            voice_client = ctx.voice_client
            voice_client.play(source, after=lambda x=None: asyncio.run(checkQueue(ctx)))


client.run(TOKEN)
