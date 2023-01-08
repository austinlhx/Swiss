import random, asyncio
from discord import Message, Embed

BOT_COMMANDS = 1047618915343282196
BOT_TESTING = 1060934072832102450

def add_misc_features(client): 
    
    @client.command()
    async def coinflip(ctx):
        choice = random.randint(1,2)
        await ctx.send("Flipping a coin")
        await asyncio.sleep(2)
        if choice == 1:
            await ctx.send("Heads!")
        else:
            await ctx.send("Tails!")
    
    @client.command()
    async def poll(ctx):
        if ctx.channel.id != BOT_COMMANDS and ctx.channel.id != BOT_TESTING:
            return 
        prompt_msg = "Enter a prompt: "
        await ctx.send(prompt_msg)
        def correct_author(m):
            return m.author == ctx.author
        
        prompt = await client.wait_for('message', check=correct_author)
        
        await ctx.send("Enter options separated by commas up to 5 options (eg: yes,no,maybe ): ")
        option_message = await client.wait_for('message', check=correct_author)
        options = option_message.content.split(",")

        await ctx.send("Enter a channel id to send it in: ")
        channel = await client.wait_for('message', check=correct_author)
        send_channel = client.get_channel(int(channel.content))
            
        embed_msg = Embed(title="Poll", description=prompt.content)
        max_options = min(len(options), 5)
        for i in range(max_options):
            option_name = "Option " + str(i) + ":"
            embed_msg.add_field(name=option_name, value=options[i], inline=False)

        msg = await send_channel.send(embed=embed_msg)
        emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
        for i in range(max_options):
            await msg.add_reaction(emojis[i])


    
    