import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio
from discord import FFmpegPCMAudio

intents = discord.Intents.all()
intents.voice_states = True
intents.messages = True
intents.emojis = True
intents.typing = True

bot = commands.Bot(command_prefix='?', intents=intents)

async def wait_for_audio_finish(voice_client):
    # Wait until the bot starts playing audio
    await voice_client.wait_until_playing()

    # Wait until the bot stops playing audio
    await voice_client.wait_until_done()

async def disconnect_after_playing(voice_client):
    # Disconnect from the voice channel
    await voice_client.disconnect()

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='play', help='Plays music in voice channel')
async def play(ctx, *, query: str):
    # Check if the bot is already in a voice channel
    voice_client = ctx.guild.voice_client
    if voice_client is None:
        # Check if the user is in a voice channel
        if ctx.author.voice is None or ctx.author.voice.channel is None:
            await ctx.send("You are not connected to a voice channel")
            return

        voice_channel = ctx.author.voice.channel

        print(f"Attempting to join voice channel: {voice_channel.name} ({voice_channel.id})")
        
        # Join the voice channel
        try:
            voice_client = await voice_channel.connect()
            print("Successfully joined voice channel")
        except Exception as e:
            print(f"Failed to join voice channel: {e}")
            await ctx.send("Failed to join voice channel")
            return

    # Download video audio using youtube_dl
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(query, download=False)
            title = info['title']
            url = info['formats'][0]['url']
        except youtube_dl.DownloadError as e:
            print(f"Failed to extract information from URL: {e}")
            await ctx.send("Failed to process the link. Please try again.")
            return

    print(f"Now playing: {title}")
    await ctx.send(f"Now playing: {title}")

    # Play the audio stream in the voice channel with reconnect options
    source = FFmpegPCMAudio(source=url, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", options="-vn")
    voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(disconnect_after_playing(voice_client), bot.loop))

    # Wait for the audio to finish playing
    try:
        await asyncio.wait_for(wait_for_audio_finish(voice_client), timeout=300)
    except asyncio.TimeoutError:
        print("Audio playback timed out")
        await ctx.send("Audio playback timed out")

@bot.command(name='test', help='Responds with "it is working now"')
async def test(ctx):
    await ctx.send("It is working now")

@bot.command(name='leave', help='Leaves the voice channel')
async def leave(ctx):
    # Check if the bot is in a voice channel
    voice_client = ctx.guild.voice_client
    if voice_client is not None and voice_client.is_connected():
        # Disconnect from the voice channel
        await voice_client.disconnect()
        print("Left voice channel")
    else:
        await ctx.send("I'm not connected to a voice channel")

@bot.command(name='stop', help='Stops playing music')
async def stop(ctx):
    voice_client = ctx.guild.voice_client
    if voice_client is not None and voice_client.is_playing():
        voice_client.stop()
        print("Stopped playing")
        await ctx.send("Stopped playing")
    else:
        await ctx.send("I'm not playing anything")

@bot.command(name='insert', help='Inserts a file and plays it in the voice channel')
async def insert(ctx, *, filename: str):
    if ctx.message.attachments:
        attachment = ctx.message.attachments[0]
        if attachment.filename.endswith('.mp3'):
            await attachment.save(attachment.filename)
            voice_client = ctx.guild.voice_client
            if voice_client is None:
                await ctx.send("I'm not connected to a voice channel")
            else:
                source = discord.FFmpegPCMAudio(attachment.filename)
                voice_client.play(source)
                await ctx.send(f"Now playing: {attachment.filename}")
        else:
            await ctx.send("The file format is not supported. Please upload an MP3 file.")
    else:
        await ctx.send("Please upload a file.")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found. Use ?help to see available commands.")

@bot.event
async def on_voice_state_update(member, before, after):
    if bot.voice_clients and not any(member in vc.channel.members for vc in bot.voice_clients):
        for vc in bot.voice_clients:
            await vc.disconnect()

# Replace 'YOUR_TOKEN_HERE' with your actual bot token, in this case I used an external file.

token =  ''
file_path = 'token.txt'
try:
    with open(file_path,'r') as file:
        token = file.read()
except FileNotFoundError:
    print(f"{file_path} not found.")

bot.run(token)
