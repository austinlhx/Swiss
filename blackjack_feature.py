from blackjack import Blackjack, POSTGRES
from blackjack_view import CACHE
import discord
from discord.ext import commands, tasks

import datetime, psycopg


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

