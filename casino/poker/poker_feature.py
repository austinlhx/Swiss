from casino.poker.poker import Poker

def add_poker_feature(client):

    @client.command()
    async def poker(ctx, *args):
        
        if len(args) != 2:
            return await ctx.send("Please re-enter command $poker {small_blind} {buy_in} ")
            
        try:
            small_blind = int(args[0])
            buy_in = int(args[1])
        except Exception:
            return await ctx.send("Please enter a number as an argument.")
            

        if small_blind < 5:
            return await ctx.send("Please enter a small blind value >= 5")
        if buy_in < small_blind * 20:
            return await ctx.send("Please enter a buy_in value of small blind * 20")
        
        leader = ctx.author

        new_game = Poker(small_blind, client, buy_in, leader, ctx)
        credits_available = new_game.extract_user_credits(leader.id)
        if credits_available < new_game.credits:
            return await ctx.send("You do not have sufficient credits to create a game!")

        await new_game.start_game()

    

