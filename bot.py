import discord
from discord.ext import commands
from discord import app_commands
from googletrans import Translator
import json
import asyncio
import yt_dlp

#Initializing the bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

#Adding the token using config.json
with open('config.json', 'r') as cfg:
    data = json.load(cfg)

#Intializing the Google ranslate API
translator = Translator()

bot = commands.Bot(command_prefix='.', intents=intents)
#Since I want to use slash commands, I tried to not add a command prefix
#But couldn't find a reliable way to do that in the brief search I did

#Defining what to do on events
@bot.event
async def on_ready():
    print(f'Successfully logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} commands')
    except Exception as e:
        print(e)

#Defining slash commands
#Translate command
@bot.tree.command(name="translate", description="Translate text to a specified language")
async def translate(interaction: discord.Interaction, text: str, dest_lang: str):
    translation = translator.translate(text, dest=dest_lang)
    await interaction.response.send_message(f'Translated to {dest_lang}: {translation.text}')

#Reminder/Alarm command
@bot.tree.command(name="reminder", description="Set a reminder")
async def reminder(interaction: discord.Interaction, duration_in_minutes: int, label: str):
    await interaction.response.send_message(f"Reminder set for {duration_in_minutes} minutes for: {label}")
    await asyncio.sleep(duration_in_minutes*60)
    await interaction.followup.send(f"Reminder: {label}")

#Music command
@bot.tree.command(name="play", description="Play a song/audio clip in a voice channel")
async def play(interaction: discord.Interaction, query: str, channel_name: str):
    #Defer the interaction response
    await interaction.response.defer()
    
    #Find the voice channel
    channel = discord.utils.get(interaction.guild.voice_channels, name=channel_name)
    if channel is None:
        await interaction.followup.send(f"Voice channel '{channel}' not found.")
        return
    
    #If channel name is valid, connect to channel
    vc = await channel.connect()

    #Time to find video on youtube
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True
    }
    
    #Extracting the details of the search result fetched
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
        url = info['formats'][0]['url']
        title = info['title']
    
    await interaction.followup.send(f"Playing: {title} in {channel_name}")

    #Play the audio
    vc.play(discord.FFmpegPCMAudio(url))
    while vc.is_playing():
        await asyncio.sleep(1)
    
    #Disconnect once music is over
    await vc.disconnect()

#Starting the bot
bot.run(data["token"])