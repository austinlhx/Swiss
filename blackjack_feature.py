from blackjack import Blackjack, POSTGRES
import discord
from discord.ext import commands, tasks

import datetime, psycopg

CACHE = {}
DAILY_CLAIMS = {}

def add_blackjack_feature(client): 
    
    create_credit_table()

    @client.command(name='blackjack', aliases=['bj'])
    async def blackjack(ctx, *args):
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
        user = str(ctx.author.id)
            
        if DAILY_CLAIMS.get(user):
            await ctx.send("You already have claimed todays daily, please try again on " + str(DAILY_CLAIMS[user]))
            return

        curr_time = datetime.datetime.now()
        tomorrow = curr_time + datetime.timedelta(days=1)
        DAILY_CLAIMS[user] = tomorrow

        with psycopg.connect(POSTGRES) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM credits WHERE user_id = %s",
                    (user,)
                )
                user_credits = cur.fetchone()
                if not user_credits:
                    cur.execute(
                        "INSERT INTO credits (user_id, credit) VALUES (%s, %s)",
                        (user, 1000))
                else:
                    cur.execute(
                        "UPDATE credits SET credit = credit + 1000 WHERE user_id = %s",
                        (user,)
                    )
                cur.execute(
                    "SELECT * FROM credits WHERE user_id = %s",
                    (user,)
                )
                user_credits = cur.fetchone()
                credit_count = user_credits[2]

            conn.commit()

        await ctx.send("Credits acquired, you now have " + str(credit_count) + " credits.")
    
    @tasks.loop(minutes=1)
    async def daily_deletion():
        curr_time = datetime.datetime.now()
        for user, time in DAILY_CLAIMS:
            if curr_time >= time:
                del DAILY_CLAIMS[user]
                break
    
    @client.command()
    async def leaderboard(ctx):
        with psycopg.connect(POSTGRES) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM credits ORDER BY credit DESC LIMIT 5;"
                )
                top_5 = cur.fetchall()
        
        top_5_str = ""
        for i, item in enumerate(top_5):
            _, user_id, credit = item
            discord_user = await client.fetch_user(user_id)
            username = str(discord_user.name)
            leaderboard_str = str(i+1) + ". " + username + ": " + str(credit) + " credits"
            top_5_str += leaderboard_str + "\n"
        
        embed_msg = discord.Embed(title="Leaderboard", description=top_5_str)
        await ctx.send(embed=embed_msg)

    @client.command()
    async def credits(ctx):
        user = ctx.author.id

        with psycopg.connect(POSTGRES) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM credits WHERE user_id = %s",
                    (user,)
                )
                extracted_user = cur.fetchone()
                if not extracted_user:
                    await ctx.send("You currently have 0 credits.")
                else:
                    await ctx.send("You currently have " + str(extracted_user[2]) + " credits.")
        
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
    
def create_credit_table():
    with psycopg.connect(POSTGRES) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                    CREATE TABLE IF NOT EXISTS credits (
                        id serial PRIMARY KEY,
                        user_id bigint,
                        credit integer)
            """)
        conn.commit()

