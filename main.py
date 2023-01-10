import discord
from discord.utils import get
from discord.ext import commands
import os, logging

from features.trophy_feature import add_trophy_feature
from features.user_info_feature import add_user_info_feature
from features.misc_feature import add_misc_features
from casino.gambling import add_gambling_features

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]

def main():
    logging.basicConfig(level = logging.INFO)

    intents = discord.Intents.default()
    intents.message_content = True
    intents.reactions = True
    client = commands.Bot(intents=intents, command_prefix='$')

    @client.event
    async def on_ready():
        logging.info("Logged on")
    
    add_trophy_feature(client)
    add_user_info_feature(client)
    add_misc_features(client)
    add_gambling_features(client)
    
    client.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
