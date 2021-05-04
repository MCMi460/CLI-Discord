import discord
from discord.ext import commands, tasks
import sys
import os
import threading
import asyncio
import requests
from pydub import AudioSegment
from pydub.playback import play
from setup import username, startup_server_id, token

name = None
avatar = None
startbot = False
running_bot = False
currentserver = None
currentchannel = None
msgsend = None
dnd = False

notification = AudioSegment.from_file('resources/discord-notification.mp3', format="mp3")

class Background(threading.Thread):
    def run(self,*args,**kwargs):
        intents = discord.Intents.default()
        intents.members = True

        global startbot
        global e

        while True:
            if startbot:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                e = asyncio.Event()
                loop = asyncio.get_event_loop()

                bot = commands.Bot(command_prefix='?',intents=intents)

                @bot.event
                async def on_ready():
                    global running_bot
                    running_bot = True
                    global username
                    global avatar
                    global name
                    global currentserver
                    global currentchannel

                    if startup_server_id:
                        currentserver = discord.utils.get(bot.guilds, id=startup_server_id)
                    if not currentserver:
                        currentserver = bot.guilds[0]
                    currentchannel = currentserver.text_channels[0]
                    print(f"Joined {currentserver} :: {currentchannel}")

                    for guild in bot.guilds:
                        user = discord.utils.get(guild.members, name=username.split("#")[0], discriminator=username.split("#")[1])
                        if user:
                            break
                    if not user:
                        name = "Guest"
                        avatar = requests.get("https://discord.com/assets/28174a34e77bb5e5310ced9f95cb480b.png").content
                    else:
                        name = user.name
                        avatar = requests.get(user.avatar_url).content
                    sendmsg.start()

                @tasks.loop(seconds=1)
                async def sendmsg():
                    global msgsend
                    if msgsend:
                        webhook = await currentchannel.create_webhook(name=name, avatar=avatar)
                        await webhook.send(msgsend)
                        await webhook.delete()
                        msgsend = None

                @bot.event
                async def on_message(message):
                    if message.channel.id == currentchannel.id and message.author != bot.user:
                        if message.author.bot:
                            if message.author.name == name:
                                return
                        if message.attachments:
                            content = f"{message.author.display_name}: {message.content}\nAttachments:"
                            for attachment in message.attachments:
                                content = f"{content}\n{attachment.filename} (URL: {attachment.url})"
                            print()
                            print("\033[A                             ")
                            print(f"\033[A{content}")
                        else:
                            print()
                            print("\033[A                             ")
                            print(f"\033[A{message.author.display_name}: {message.content}")
                            print()
                            print("\033[A>>>\033[A")
                        print()
                        print("\033[A>>>\033[A")
                        if not dnd:
                            play(notification)

                async def wait():
                    await e.wait()
                    print('stope')
                    await bot.logout()
                    loop.stop()

                async def runbot():
                    await bot.start(token)

                loop.create_task(runbot())
                loop.create_task(wait())
                loop.run_forever()
                loop.close()

                running_bot = False
                startbot = False

task = Background()
task.daemon = True
task.start()

while True:
    cin = input(">>> ")
    print("\033[A                             \033[A")
    if cin.startswith("."):
        cin = cin.replace(".","").lower()
        if cin.startswith("connect"):
            if running_bot:
                print("The bot is already running!")
            else:
                startbot = True
                while True:
                    if running_bot:
                        break
        elif cin.startswith("dnd"):
            dnd = not dnd
        elif cin.startswith("stop") or cin.lower().startswith("exit"):
            sys.exit("Thank you for using Delta!")
    else:
        msgsend = cin
        print(f"<{name}>: {cin}")
