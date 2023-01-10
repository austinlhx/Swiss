import discord
from discord.utils import get
from discord.ext import commands

CHANNEL_ID = 1052440965127864360

def add_trophy_feature(client):

    @client.event
    async def on_raw_reaction_add(payload):
        channel = client.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        reaction = get(message.reactions, emoji="🏆")

            
        if reaction and reaction.count >= 5:
            send_channel = client.get_channel(CHANNEL_ID)
            async for old_msg in send_channel.history(limit=10):
                if old_msg.embeds[0].url == message.jump_url:
                    return

            attached_link = "**[Link](" + message.jump_url + ")**"

            embed_message = discord.Embed(description=message.author, url = message.jump_url, colour=discord.Colour.blue())
            embed_message.set_thumbnail(url=message.author.display_avatar)
            if message.content:
                embed_message.add_field(name="Message", value=message.content, inline=True)
            embed_message.add_field(name="Channel", value=channel.mention, inline=True)
            embed_message.add_field(name="Jump To", value=attached_link, inline=True)

            for attachment in message.attachments:
                if attachment.content_type.startswith("video"):
                    embed_message.add_field(name="Video Link", value=attachment)
                else:
                    embed_message.set_image(url=attachment)
                
                
            embed_message.set_footer(text=message.created_at)

            await send_channel.send(embed=embed_message)