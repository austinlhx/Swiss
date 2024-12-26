import discord
from discord.utils import get
from discord.ext import commands
from urllib.parse import urlparse
import os, logging, redis

from features.trophy_feature import add_trophy_feature
from features.user_info_feature import add_user_info_feature
from features.misc_feature import add_misc_features
from features.music_feature import add_music_features
from casino.gambling import add_gambling_features

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
REDISCLOUD_URL = os.environ["REDISCLOUD_URL"]

def main():
    logging.basicConfig(level = logging.INFO)

    intents = discord.Intents.default()
    intents.message_content = True
    intents.reactions = True
    client = commands.Bot(intents=intents, command_prefix='$')
    url = urlparse(REDISCLOUD_URL)
    redis_client = redis.Redis(host=url.hostname, port=url.port, password=url.password)

    @client.event
    async def on_ready():
        logging.info("Logged on")
    
    add_trophy_feature(client)
    # add_user_info_feature(client)
    add_misc_features(client)
    add_gambling_features(client, redis_client)
    # add_music_features(client)
    
    client.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
