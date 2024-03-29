import discord
from casino.roulette.roulette import Roulette

GAMBLING_CHANNEL = 1047620089496744020
BOT_TESTING = 1060934072832102450

def add_roulette_feature(client):

    @client.command()
    async def roulette(ctx, *args):
        if ctx.channel.id != GAMBLING_CHANNEL and ctx.channel.id != BOT_TESTING:
            return 
        
        if len(args) > 1 or len(args) == 0:
            await ctx.send("Please re-enter command $roulette {wager_amount}")
            return
        try:
            credits_bet = int(args[0])
        except Exception:
            await ctx.send("Please enter a number as an argument.")
            return

        if credits_bet == 0:
            await ctx.send("Please enter a value > 0")
            return
        
        player = ctx.author

        new_game = Roulette(credits_bet, player, ctx)

        credits_available = await new_game.wager_credits(player.id)

        if not credits_available:
            return

        await new_game.start_game()