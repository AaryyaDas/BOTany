import discord
from discord.ext import commands
from discord import app_commands
from googletrans import Translator
import json
import asyncio

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

#Starting the bot
bot.run(data["token"])