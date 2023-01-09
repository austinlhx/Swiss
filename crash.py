from discord import Embed, Color
from crash_view import CrashView
from casino import Casino
import random, asyncio, os, psycopg, logging

POSTGRES = os.environ["DATABASE_URL"]

class Crash(Casino):
    def __init__(self, credits, client, ctx):
        super().__init__(credits, client, ctx)
        self.view = None
        self.current_multiplier = 1.0
        self.crashed = False
        self.cashed_out = False
        self.msg = None
    
    async def start_game(self):
        embed_msg = Embed(title="Crash", color=Color.blue())
        embed_msg.set_author(name=self.ctx.author.name, icon_url=self.ctx.author.display_avatar)

        embed_msg.add_field(name="Your Bet: ", value=str(self.credits) + " credits", inline=False)
        embed_msg.add_field(name="Current Multiplier: ", value= "x" + str(self.current_multiplier), inline=False)
        embed_msg.set_image(url="https://media4.giphy.com/media/JmUd8L6SMdTrriXSEc/giphy.gif?cid=ecf05e47knq7hlosyhuyy5t6calld7yh0xtvnywtdc4o1h1h&rid=giphy.gif&ct=g")

        self.view = CrashView(self.ctx, embed_msg, self)

        self.msg = await self.ctx.send(embed=embed_msg, view=self.view)
        await asyncio.sleep(1)
        await self.increase_multiplier()
    
    async def increase_multiplier(self):
        while not self.crashed and not self.cashed_out:
            rand_num = random.randint(1, 10)
            if rand_num == 7:
                self.crashed = True
                break
            
            self.current_multiplier += 0.1
            self.current_multiplier = round(self.current_multiplier, 1)
            self.view.embed.set_field_at(index=1, name="Current Multiplier: ", value= "x" + str(self.current_multiplier))

            await self.msg.edit(embed=self.view.embed, view=self.view)
            await asyncio.sleep(1)
        if self.cashed_out:
            credits_won = int(self.credits * self.current_multiplier)
            self.multiplied_credits(credits_won)
        else:
            await self.crashed_view()
        
    async def crashed_view(self):
        lost_str = "CRASHED! Lost: " + str(self.credits) + " credits"
        self.view.embed.add_field(name="Results: ", value=lost_str, inline=False)
        self.view.embed.set_image(url="https://j.gifs.com/mGDBk1.gif")
        self.view.embed.color = Color.red()
        await self.msg.edit(embed=self.view.embed, view=None)