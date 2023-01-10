from casino.blackjack.blackjack_feature import add_blackjack_feature
from casino.crash.crash_feature import add_crash_feature
from casino.blackjack.blackjack import POSTGRES
from discord.ext import commands, tasks
from discord import Embed, Color
import datetime, psycopg

DAILY_CLAIMS = {}

def add_gambling_features(client):
    create_credit_table()

    add_blackjack_feature(client)
    add_crash_feature(client)

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
    async def commands(ctx):
        embed = Embed(title="Command List", color=Color.blue())
        embed.add_field(name="Blackjack", value="$blackjack {wager_amount}", inline=False)
        embed.add_field(name="Crash", value="$crash {wager_amount}", inline=False)
        embed.add_field(name="Leaderboard", value="$leaderboard", inline=False)
        embed.add_field(name="Daily Credits", value="$daily", inline=False)
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