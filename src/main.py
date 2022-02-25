
#---------------------------------------------------------------#
#--------------{This code belongs to Xriss_Xross}---------------#
#---------------------------------------------------------------#
#--------{If you for whatever reason use any of my code}--------#
#----------------------{remember it's MIT}----------------------#
#---------------------------------------------------------------#
#---{Some of this code was developed with the help of Prlxx}----#
#---------------{Try not to blantantly plagarise}---------------#
#---------------------------------------------------------------#

import json
import random
import discord
from pytube import Playlist
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
with open("src\quotes.json") as json_file:
	quotes = json.load(json_file)

TOKEN = os.getenv("TOKEN")
PREFIX = os.getenv("PREFIX")
client = commands.Bot(command_prefix=PREFIX)
client.remove_command('help')

#-------------------------{BOT_BASICS}--------------------------#

@client.event
async def on_ready():
    print('Bot Online:{0.user}'.format(client))
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="everyone"))


@client.command(name="ping")
async def ping(ctx):
    await ctx.send(f"Pong! Latency: {round(client.latency * 1000)} ms")


@client.command(aliases=["HELP", "h", "H"])
async def help(ctx):
    await ctx.channel.send("No")

#-------------------------{YOUTUBE_BOT}-------------------------#

LIMIT = 5 # how many titles will be searched through the ~search command
QUEUE = []

async def checkQueue(ctx): # y is passed to determine whether the first song should be skipped or not
    if QUEUE != []:
        try:
            with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                voice_client = ctx.voice_client
                info = ydl.extract_info(QUEUE[0][1], download=False)
                url2 = info["formats"][0]["url"]
                source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
                voice_client.play(source, after=lambda x=None: asyncio.run(checkQueue(ctx)))
                embed = discord.Embed(color=0x22BBBB)
                embed.add_field(name=f"Now playing: {QUEUE[0][0]} :headphones:", value=f"{QUEUE[0][1]}", inline=False)
                await ctx.send(embed=embed)
        except:
            QUEUE.pop(0)
            await ctx.send("There was a problem playing that song so the next song is playing.")
            with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                voice_client = ctx.voice_client
                info = ydl.extract_info(QUEUE[0][1], download=False)
                url2 = info["formats"][0]["url"]
                source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
                voice_client.play(source, after=lambda x=None: asyncio.run(checkQueue(ctx)))
                embed = discord.Embed(color=0x22BBBB)
                embed.add_field(name=f"Now playing: {QUEUE[0][0]}", value="f{QUEUE[0][1]}", inline=False)
                await ctx.send(embed=embed)


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
    if args[0] is None:
        pass
    elif args[0].startswith("https://www.youtube.com/watch?v="): # specific video
        try:
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
                    embed = discord.Embed(color=0x22BBBB)
                    embed.add_field(name=f"Added to queue: {songName}", value=songLink, inline=False)
                    await ctx.send(embed=embed)
        except:
            await ctx.send("Please make sure your request is a youtube link or an actual title of a youtube video")
        
    elif args[0].startswith("https://www.youtube.com/playlist?list="): # playlist queueing
        try:
            play_list = Playlist(args[0])
            voice_client = ctx.voice_client
            if len(play_list) == 0:
                await ctx.send("I couldn't find any songs in that playlist or I couldn't find the playlist")
            else:
                i = len(QUEUE)
                for video in play_list.videos:
                    name = video.title
                    QUEUE.append([name])
                for link in play_list:
                    QUEUE[i].append(link)
                    i += 1
                await ctx.send(f"{len(play_list)} songs added to the queue")
                if ctx.voice_client.is_playing():
                    pass
                else:
                    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                        info = ydl.extract_info(QUEUE[0][1], download=False)
                        url2 = info["formats"][0]["url"]
                        source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
                        voice_client.play(source, after=lambda x=None: asyncio.run(checkQueue(ctx)))
                        embed = discord.Embed(color=0x22BBBB)
                        embed.add_field(name=f"Now playing: {QUEUE[0][0]} :headphones:", value=songLink, inline=False)
                        await ctx.send(embed=embed)
        except:
            await ctx.send("Please make sure your request is a youtube link")

    else: # name of the youtube video is given
        try:
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
                    embed = discord.Embed(color=0x22BBBB)
                    embed.add_field(name=f"Added to queue: {songName}", value=songLink, inline=False)
                    await ctx.send(embed=embed)
        except:
            await ctx.message.send("Please make sure your request is a youtube link or an actual title of a youtube video")


@client.command(aliases=["SEARCH", "SE", "se"])
async def search(ctx, *args):
    if ctx.author.voice is None:
        await ctx.send("You aren't in a voice channel")
    else:
        searchQueryArgs = " ".join(args)
        searchQuery = VideosSearch(searchQueryArgs, limit=LIMIT)
        embed = discord.Embed(color=0x22BBBB)
        tempQUEUE = []
        for i in range(5):
            songName = searchQuery.result()["result"][i]["title"]
            songLink = "https://www.youtube.com/watch?v=" + searchQuery.result()["result"][i]["id"]
            embed.add_field(name=f"{i + 1}. {songName}", value=songLink, inline=False)
            tempQUEUE.append([songName, songLink])
        await ctx.send(embed=embed)
        await ctx.send("Which video do you want to queue?")
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel
        try:
            msg = await client.wait_for("message", check=check, timeout=30)
            msgContent = int(msg.content)
            QUEUE.append(tempQUEUE[msgContent - 1])
            voice_client = ctx.voice_client
            channel = ctx.author.voice.channel
            if ctx.voice_client is None:
                await channel.connect()
            else:
                await ctx.voice_client.move_to(channel)
            if ctx.voice_client.is_playing():
                pass
            else:
                with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(QUEUE[0][1], download=False)
                    url2 = info["formats"][0]["url"]
                    source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
                    voice_client = ctx.voice_client
                    voice_client.play(source, after=lambda x=None: asyncio.run(checkQueue(ctx)))
        except Exception as e:
            print(e)
            await ctx.send("Please give me a valid option withing 30s next time")

    
@client.command(aliases=["q", "Q", "QUEUE"])
async def queue(ctx):
    if len(QUEUE) == 0:
        await ctx.send("It doesn't look like there is a queue right now. Try **~play** to add some beats to the queue :headphones:")
    else:
        embed = discord.Embed(color=0x22BBBB)
        if len(QUEUE) > 9:
            x = 9
        else:
            x = len(QUEUE)
        for i in range(x):
            embed.add_field(name=QUEUE[i][0], value=QUEUE[i][1], inline=False)
    await ctx.send(embed=embed)


@client.command(aliases=["cq", "CQ", "CLEARQUEUE", "clearq", "CLEARQ"])
async def clearqueue(ctx):
    if QUEUE != []:
        for i in QUEUE:
            QUEUE.pop(i + 1)
            voice_client = ctx.voice_client
    else:
        await ctx.send("There is currently no audio playing in the voice channel")


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
        await ctx.send("There is currently no audio playing in the voice channel")


@client.command(aliases=["re", "RESUME", "RE"])
async def resume(ctx):
    voice_client = ctx.voice_client
    if voice_client.is_paused():
        voice_client.resume()
    else:
        await ctx.send("There is currently no audio paused")


@client.command(aliases=["summon", "SUMMON", "j", "J", "JOIN", "connect", "CONNECT"])
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

#--------------------------{QUOTEBOOK}--------------------------#

@client.command(aliases=["RANDOMQ", "rq", "RQ"])
async def randomq(ctx, *args):
    if args[0] == "all":
        randomqgen = random.randint(1, 24)
    elif args[0] == "tommy" or args[0] == "Tommy":
        randomqgen = random.randint(1,8)
    elif args[0] == "scam" or args[0] == "Scam":
        randomqgen = random.randint(9,17)
    elif args[0] == "dream" or args[0] == "Dream":
        randomqgen = random.randint(18,26)
    file = discord.File("{filename}".format(filename=quotes["quotes"][randomqgen]["link"]),filename=quotes["quotes"][randomqgen]["link"])
    embed = discord.Embed(title="Clip:",description=quotes["quotes"][randomqgen]["quote"],color=0x22BBBB)
    embed.set_footer(text=f"do {PREFIX}rq for another! 🔥 ")
    await ctx.channel.send(embed=embed, file=file)


@client.command(aliases=["qb", "QB", "QUOTEBOOK"])
async def quotebook(ctx, *args):
    embed = discord.Embed(title="Quote Book :book:",description="*From your's truly*",color=0x22BBBB)
    if args[0] == "tommy" or args[0] == "TOMMY":
        range1 = 0
        range2 = 9
    elif args[0] == "scam" or args[0] == "SCAM":
        range1 = 9
        range2 = 18
    randomArray = []
    for i in range(range1, range2):
        randomSunZu = random.randint(0,35)
        while randomSunZu in randomArray:
            randomSunZu = random.randint(0,35)
        randomArray.append(randomSunZu)
        with open("src/sunZuQuotes.txt") as f:
            sunZuquotes = [line.rstrip('\n') for line in f]
            sunZuQuote = sunZuquotes[randomSunZu]
        quoteName = quotes["quotes"][i]["quote"]
        embed.add_field(name=f"No. {i+1} {quoteName}",value = f"{sunZuQuote} -Sun Zu" ,inline=False)
    await ctx.channel.send(embed=embed)


@client.command(aliases=["SEEK"])
async def seek(ctx, *args):
    quoteNo = int(args[0]) - 1
    file = discord.File("{filename}".format(filename=quotes["quotes"][quoteNo]["link"]),filename=quotes["quotes"][quoteNo]["link"])
    embed = discord.Embed(title="Clip:",description=quotes["quotes"][quoteNo]["quote"],color=0x22BBBB)
    embed.set_footer(text=f"do {PREFIX}seek for another! 🔥 ")
    await ctx.channel.send(embed=embed, file=file)

client.run(TOKEN)
