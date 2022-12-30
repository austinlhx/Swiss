import random, asyncio

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