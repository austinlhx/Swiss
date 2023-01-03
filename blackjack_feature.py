from deck_of_cards import deck_of_cards
from blackjack import Blackjack, CREDITS_FILE
import discord
from discord.ext import commands, tasks

import json, datetime, heapq

CACHE = {}
DAILY_CLAIMS = {}

def add_blackjack_feature(client): 
    
    @client.command(name='blackjack', aliases=['bj'])
    async def blackjack(ctx, *args):
        if len(args) > 1 or len(args) == 0:
            await ctx.send("Please re-enter command $blackjack {wager_amount}")
            return
        
        credits_bet = int(args[0])

        if credits_bet == 0:
            await ctx.send("Please enter a value > 0")
            return

        new_game = Blackjack(credits_bet, ctx.author, ctx)
        

        if CACHE.get(ctx.author):
            await ctx.send("You are already in an on going game. Please hit or stand.")
            return

        credits_available = await new_game.wager_credits()

        if not credits_available:
            return

        CACHE[ctx.author] = new_game

        game_ended = await new_game.start_game()

        if game_ended:
            del CACHE[ctx.author]
    
    @client.command()
    async def daily(ctx):
        with open(CREDITS_FILE, 'r') as json_file:
            data = json.load(json_file)
            user = str(ctx.author.id)

        if DAILY_CLAIMS.get(user):
            await ctx.send("You already have claimed todays daily, please try again on " + str(DAILY_CLAIMS[user]))
            return

        curr_time = datetime.datetime.now()
        tomorrow = curr_time + datetime.timedelta(days=1)
        DAILY_CLAIMS[user] = tomorrow

        if data['credits'].get(user):
            data['credits'][user] += 1000
        else:
            data['credits'][user] = 1000

        with open(CREDITS_FILE, 'w') as json_file:    
            json_data = json.dumps(data)
            json_file.write(json_data)

        await ctx.send("Credits acquired, you now have " + str(data['credits'][user]) + " credits.")
    
    @tasks.loop(minutes=1)
    async def daily_deletion():
        curr_time = datetime.datetime.now()
        for user, time in DAILY_CLAIMS:
            if curr_time >= time:
                del DAILY_CLAIMS[user]
                break
    
    @client.command()
    async def leaderboard(ctx):
        with open(CREDITS_FILE, 'r') as json_file:
            data = json.load(json_file)
            user_credits = data['credits']
        
        heap = []
        for user, credit in user_credits.items():
            heapq.heappush(heap, (-credit, user))
        
        top_5 = []
        heap_size = len(heap)

        if heap_size > 5:
            heap_size = 5

        for _ in range(heap_size):
            credit, user = heapq.heappop(heap)
            top_5.append((user, -credit))
        
        top_5_str = ""
        for i, item in enumerate(top_5):
            discord_user = await client.fetch_user(item[0])
            username = str(discord_user.name)
            leaderboard_str = str(i+1) + ". " + username + ": " + str(item[1]) + " credits"
            top_5_str += leaderboard_str + "\n"
        
        embed_msg = discord.Embed(title="Leaderboard", description=top_5_str)
        await ctx.send(embed=embed_msg)

    @client.command()
    async def credits(ctx):
        with open(CREDITS_FILE, 'r') as json_file:
            data = json.load(json_file)
            user = str(ctx.author.id)
            credit_count = data['credits'].get(user, 0)

        await ctx.send("You currently have " + str(credit_count) + " credits.")
        
    @client.command()
    async def hit(ctx):
        if not CACHE.get(ctx.author):
            await ctx.send("You are not currently in an active game, please enter command $blackjack {wager_amount} to start game.")
            return

        curr_game = CACHE[ctx.author]
        curr_game.can_double = False

        new_card = curr_game.deck.deck.pop(0)
        curr_game.user_cards.append(new_card)

        curr_total = curr_game.hand_total(curr_game.user_cards)
        
        if curr_total == 21:
            await ctx.send("You now have 21")
            await stand(ctx)
        elif curr_total < 21:
            await ctx.send("You now have " + str(curr_total))
            if curr_game.doubled:
                await stand(ctx)
        else:
            await ctx.send("You now have " + str(curr_total))
            await ctx.send("Player busts.")
            del CACHE[ctx.author]
    
    @client.command()
    async def double(ctx):
        if not CACHE.get(ctx.author):
            await ctx.send("You are not currently in an active game, please enter command $blackjack {wager_amount} to start game.")
            return

        curr_game = CACHE[ctx.author]
        
        if not curr_game.can_double:
            await ctx.send("You can only double on first hit.")
            return

        curr_game.doubled = True
        credits_available = await curr_game.wager_credits() 
        if not credits_available:
            curr_game.doubled = False
            return

        curr_game.credits *= 2
        
        await hit(ctx)
    
    @client.command()
    async def stand(ctx):
        if not CACHE.get(ctx.author):
            await ctx.send("You are not currently in an active game, please enter command $blackjack {wager_amount} to start game.")
            return
        
        curr_game = CACHE[ctx.author]

        curr_total = curr_game.hand_total(curr_game.dealer_cards)
        await ctx.send("Dealer reveals a " + str(curr_total))
        while curr_total <= 16:
            new_card = curr_game.deck.deck.pop(0)
            curr_game.dealer_cards.append(new_card)
            curr_total = curr_game.hand_total(curr_game.dealer_cards)
            await ctx.send("Dealer now has " + str(curr_total))
        
        user_total = curr_game.hand_total(curr_game.user_cards)

        if curr_total > 21:
            await curr_game.double_credits()
            await ctx.send("Dealer busts, player wins. Congratulations!")
        elif curr_total <= 21 and curr_total > user_total:
            await ctx.send("Dealer wins.")
        elif curr_total <= 21 and curr_total < user_total:
            await curr_game.double_credits()
            await ctx.send("Player wins " + str(curr_game.credits) + " credits, congratulations!")
        else:
            await curr_game.push_credits()
            await ctx.send("Player pushes.")
        
        del CACHE[ctx.author]

