import random, asyncio, wavelink, os
from discord import Message, Embed

class CustomPlayer(wavelink.Player):

    def __init__(self):
        super().__init__()
        self.queue = wavelink.Queue()

def add_music_features(client): 

    @client.event
    async def on_ready():
        client.loop.create_task(connect_node(client))
    
    async def connect_node(client):
        await client.wait_until_ready()
        await wavelink.NodePool.create_node(
            bot=client,
            host=os.environ["LAVALINK_HOSTNAME"],
            port=80,
            password=os.environ["LAVALINK_PASS"],
        )
    
    @client.event
    async def on_wavelink_node_ready(node):
        print("node is ready")
    
    @client.command()
    async def rickroll(ctx):

        vc = ctx.voice_client
        try:
            channel = ctx.author.voice.channel
        except AttributeError:
            return await ctx.send("You need to be in a channel to play this!")

        if not vc:
            vc = await ctx.author.voice.channel.connect(cls=CustomPlayer())
        else: 
            search = wavelink.YouTubeTrack(info={'identifier': 'dQw4w9WgXcQ', 'isSeekable': True, 'author': 'Rick Astley', 'length': 213000, 'isStream': False, 'position': 0, 'sourceName': 'youtube', 'title': 'Rick Astley - Never Gonna Give You Up (Official Music Video)', 'uri': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'}, id="QAAAoQIAPFJpY2sgQXN0bGV5IC0gTmV2ZXIgR29ubmEgR2l2ZSBZb3UgVXAgKE9mZmljaWFsIE11c2ljIFZpZGVvKQALUmljayBBc3RsZXkAAAAAAANACAALZFF3NHc5V2dYY1EAAQAraHR0cHM6Ly93d3cueW91dHViZS5jb20vd2F0Y2g/dj1kUXc0dzlXZ1hjUQAHeW91dHViZQAAAAAAAAAA")

            await vc.play(search)


    @client.command()
    async def disconnect(ctx):
        vc = ctx.voice_client
        if vc:
            await ctx.send(f"Bot has been disconnected by {ctx.author.name}")
            await vc.disconnect()
        else:
            await ctx.send("The bot is not currently connected to a voice channel.")


    @client.command()
    async def play(ctx, *, search: wavelink.YouTubeTrack):
        vc = ctx.voice_client
        if not vc:
            custom_player = CustomPlayer()
            vc: CustomPlayer = await ctx.author.voice.channel.connect(cls=custom_player)

        embed_msg = Embed(
                title=search.title,
                url=search.uri)
        embed_msg.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar) 

        if vc.is_playing():
            vc.queue.put(item=search)
            description = f"Queued {search.title} in {vc.channel}"
            embed_msg.add_field(name="Status", value=description)
            await ctx.send(embed=embed_msg)
        else:
            await vc.play(search)
            description=f"Playing {vc.source.title} in {vc.channel}"
            embed_msg.add_field(name="Status", value=description)
            await ctx.send(embed=embed_msg)

    @client.command()
    async def skip(ctx):
        vc = ctx.voice_client
        if vc:
            if not vc.is_playing():
                return await ctx.send("There is nothing playing.")
            if vc.queue.is_empty:
                await ctx.send(f"Music has been skipped by {ctx.author.name}")
                return await vc.stop()

            await vc.seek(vc.track.length * 1000)
            if vc.is_paused():
                await vc.resume()
        else:
            await ctx.send("The bot is not currently connected to a voice channel.")


    @client.command()
    async def pause(ctx):
        vc = ctx.voice_client
        if vc:
            if vc.is_playing() and not vc.is_paused():
                await ctx.send(f"Music has been paused by {ctx.author.name}")
                await vc.pause()
            else:
                await ctx.send("There is nothing playing.")
        else:
            await ctx.send("The bot is not connected to a voice channel")


    @client.command()
    async def resume(ctx):
        vc = ctx.voice_client
        if vc:
            if vc.is_paused():
                await ctx.send(f"Music has been resumed by {ctx.author.name}")
                await vc.resume()
            else:
                await ctx.send("Nothing is paused.")
        else:
            await ctx.send("The bot is not connected to a voice channel")