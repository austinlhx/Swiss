from casino.blackjack.blackjack_feature import add_blackjack_feature
from casino.crash.crash_feature import add_crash_feature
from casino.battle.battle_feature import add_battle_feature
from casino.roulette.roulette_feature import add_roulette_feature
from casino.blackjack.blackjack import POSTGRES
from discord.ext import commands, tasks
from discord import Embed, Color
import datetime, psycopg

DAILY_CLAIMS = {}

def add_gambling_features(client):
    create_credit_table()

    add_blackjack_feature(client)
    add_roulette_feature(client)
    add_crash_feature(client)
    add_battle_feature(client)

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
        
        embed_msg = Embed(title="Leaderboard", description=top_5_str)
        await ctx.send(embed=embed_msg)

    @client.command()
    async def credits(ctx, *args):
        if len(args) > 1:
            await ctx.send("Please re-enter command $credits {user} or $credits")
            return
        elif len(args) == 0:
            user, searched_user = ctx.author.id, None
        else:
            user = args[0]
            try:
                user = int(user[2:-1])
                searched_user = await client.fetch_user(user)
                searched_user = searched_user.name
            except Exception:
                await ctx.send("User was not found, please enter command in the form of $credits @{user}")
                return

        with psycopg.connect(POSTGRES) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM credits WHERE user_id = %s",
                    (user,)
                )
                extracted_user = cur.fetchone()
                if not extracted_user:
                    if not searched_user:
                        await ctx.send("You currently have 0 credits.")
                    else:
                        await ctx.send(searched_user + " currently has 0 credits.")
                else:
                    if not searched_user:
                        await ctx.send("You currently have " + str(extracted_user[2]) + " credits.")
                    else:
                        await ctx.send(searched_user + " currently has " + str(extracted_user[2]) + " credits.")
    
    @client.command()
    async def give(ctx, *args):
        if len(args) != 2:
            await ctx.send("Please re-enter command $give @{user} {credits}")
            return
        
        try:
            user = args[0]
            user = int(user[2:-1])
            credits_to_give = int(args[1])
            searched_user = await client.fetch_user(user)
        except Exception:
            await ctx.send("User was not found, please enter command in the form of $give @{user} {credits}")
        
        credits_available = await check_credits(ctx, credits_to_give)

        if credits_available:
            await give_credits(ctx, credits_to_give, user)
            await ctx.send("You gave " + searched_user.name + " " + str(credits_to_give) + " credits!")
        
    @client.command()
    async def commands(ctx):
        embed = Embed(title="Command List", color=Color.blue())
        embed.add_field(name="Blackjack", value="$blackjack {wager_amount}", inline=False)
        embed.add_field(name="Roulette", value="$roulette {wager_amount}", inline=False)
        embed.add_field(name="Crash", value="$crash {wager_amount}", inline=False)
        embed.add_field(name="Battle", value="$battle @{user} {wager_amount}", inline=False)
        embed.add_field(name="Leaderboard", value="$leaderboard", inline=False)
        embed.add_field(name="Daily Credits", value="$daily", inline=False)
        embed.add_field(name="Credit Count", value="$credits @{user} or $credits", inline=False)
        embed.add_field(name="Give Credits", value="$give @{user} {credit_amount}", inline=False)
        await ctx.send(embed=embed)
    
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

async def check_credits(ctx, credits):
    with psycopg.connect(POSTGRES) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM credits WHERE user_id = %s",
                (ctx.author.id,)
            )
            extracted_user = cur.fetchone()
            if not extracted_user:
                await ctx.send("You do not have any credits to give!")
                return False
                
            credits_available = int(extracted_user[2])
            if credits > credits_available:
                await ctx.send("You do not have enough credits to give, you only have " + str(credits_available) + " credits!")
                return False
    return True

async def give_credits(ctx, credits, user_id):
    with psycopg.connect(POSTGRES) as conn:
        with conn.cursor() as cur:
            cur.execute(
                    "UPDATE credits SET credit = credit - %s WHERE user_id = %s",
                    (credits, ctx.author.id)
                )
            
            cur.execute(
                "SELECT * FROM credits WHERE user_id = %s",
                (user_id,)
            )
            extracted_user = cur.fetchone()
            if not extracted_user:
                cur.execute(
                    "INSERT INTO credits (user_id, credit) VALUES (%s, %s)",
                    (user_id, credits))
            else:
                cur.execute(
                    "UPDATE credits SET credit = credit + %s WHERE user_id = %s",
                    (credits, user_id)
                )
            conn.commit()

    return True