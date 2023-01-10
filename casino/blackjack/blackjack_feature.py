from casino.blackjack.blackjack import Blackjack, POSTGRES
from casino.blackjack.blackjack_view import CACHE

GAMBLING_CHANNEL = 1047620089496744020
BOT_TESTING = 1060934072832102450

DAILY_CLAIMS = {}

def add_blackjack_feature(client): 

    @client.command(name='blackjack', aliases=['bj'])
    async def blackjack(ctx, *args):
        if ctx.channel.id != GAMBLING_CHANNEL and ctx.channel.id != BOT_TESTING:
            return 
        if len(args) > 1 or len(args) == 0:
            await ctx.send("Please re-enter command $blackjack {wager_amount}")
            return
        try:
            credits_bet = int(args[0])
        except Exception:
            await ctx.send("Please enter a number as an argument.")
            return

        if credits_bet == 0:
            await ctx.send("Please enter a value > 0")
            return

        new_game = Blackjack(credits_bet, ctx.author, ctx)
        

        if CACHE.get(ctx.author):
            await ctx.send("You are already in an on going game. Here is your on-going game:")
            await ctx.send(embed=CACHE[ctx.author].view.embed, view=CACHE[ctx.author].view)
            return

        credits_available = await new_game.wager_credits()

        if not credits_available:
            return

        CACHE[ctx.author] = new_game

        game_ended = await new_game.start_game()

        if game_ended:
            del CACHE[ctx.author]
    
