from discord import Embed, Color
from casino.roulette.roulette_view import RouletteView
from casino.casino import Casino
import random, asyncio, os, psycopg, logging

POSTGRES = os.environ["DATABASE_URL"]

class Roulette(Casino):
    def __init__(self, credits, client, ctx):
        super().__init__(credits, client, ctx)
        self.view = None
        self.current_multiplier = 1.0
        self.crashed = False
        self.cashed_out = False
        self.msg = None
    
    async def start_game(self):
        embed_msg = Embed(title="Roulette", color=Color.blue())
        embed_msg.set_author(name=self.ctx.author.name, icon_url=self.ctx.author.display_avatar)

        embed_msg.add_field(name="Your Bet:", value=str(self.credits) + " credits", inline=False)
        embed_msg.add_field(name="Picked Color: ", value="Awaiting user decision.", inline=False)
        embed_msg.add_field(name="Current Color: ", value= "🔴", inline=False)

        self.view = RouletteView(self.ctx, embed_msg, self)

        self.view.msg = await self.ctx.send(embed=embed_msg, view=self.view)