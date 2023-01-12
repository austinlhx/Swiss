from casino.rps.rps import RPS

GAMBLING_CHANNEL = 1047620089496744020
BOT_TESTING = 1060934072832102450

def add_rps_feature(client):

    @client.command()
    async def rps(ctx, *args):
        # if ctx.channel.id != GAMBLING_CHANNEL and ctx.channel.id != BOT_TESTING:
        #     return 

        if len(args) != 2:
            await ctx.send("Please re-enter command $rps  @{user} {wager_amount}")
            return
        
        try:
            credits_bet = int(args[1])
        except Exception:
            await ctx.send("Please enter a number as an argument.")
            return
        
        if credits_bet == 0:
            await ctx.send("Please enter a value > 0")
            return
        
        try:
            user = args[0]
            user_battle_id = int(user[2:-1])
            searched_user = await client.fetch_user(user_battle_id)
        except Exception:
            await ctx.send("User was not found, please enter command in the form of $rps @{user} {wager_amount}")
            return
        
        new_game = RPS(credits_bet, ctx.author, ctx, searched_user)

        player_1_credits, player_2_credits = new_game.extract_user_credits(ctx.author.id), new_game.extract_user_credits(user_battle_id)

        if player_1_credits < credits_bet:
            await ctx.send("You do not have enough credits to play rock paper scissors with!")
            return
        elif player_2_credits < credits_bet:
            await ctx.send("Player " + searched_user.name + " does not have that many credits!")
            return
        
        await new_game.start_game()

        
