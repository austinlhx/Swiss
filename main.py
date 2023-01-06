import discord
from discord.utils import get
from discord.ext import commands
import os, logging

from trophy_feature import add_trophy_feature
from user_info_feature import add_user_info_feature
from misc_feature import add_misc_features
from blackjack_feature import add_blackjack_feature

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
    add_blackjack_feature(client)
    
    client.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()