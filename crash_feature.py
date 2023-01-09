import discord
from crash import Crash

GAMBLING_CHANNEL = 1047620089496744020
BOT_TESTING = 1060934072832102450

def add_crash_feature(client):

    @client.command()
    async def crash(ctx, *args):
        if ctx.channel.id != GAMBLING_CHANNEL and ctx.channel.id != BOT_TESTING:
            return 
        
        if len(args) > 1 or len(args) == 0:
            await ctx.send("Please re-enter command $crash {wager_amount}")
            return
        try:
            credits_bet = int(args[0])
        except Exception:
            await ctx.send("Please enter a number as an argument.")
            return

        if credits_bet < 10:
            await ctx.send("Please enter a value >10 for this game")
            return
        
        new_game = Crash(credits_bet, ctx.author, ctx)

        credits_available = await new_game.wager_credits()

        if not credits_available:
            return

        await new_game.start_game()