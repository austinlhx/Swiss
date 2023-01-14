from casino.casino import Casino
from discord import Embed, Color
from casino.rps.rps_view import RPSView

import asyncio

import random

class RPS(Casino):
    def __init__(self, credits, client, ctx, challenger): 
        super().__init__(credits, client, ctx)
        self.challenger = challenger
        self.view = None
        self.msg = None

    
    async def start_game(self):
        embed_msg = Embed(title="Rock Paper Scissors", color=Color.blue())
        embed_msg.set_author(name=self.ctx.author.name, icon_url=self.ctx.author.display_avatar)
        embed_msg.add_field(name="Wager:", value=str(self.credits) + " credits", inline=False)
        embed_msg.add_field(name="Players:", value=self.ctx.author.name + " vs " + self.challenger.name, inline=False)

        challenge_str = f"{self.challenger.mention}, you have been challenged to a RPS game from {self.ctx.author.mention}. Do you accept or decline?"

        embed_msg.add_field(name="State", value=challenge_str, inline=False)

        self.view = RPSView(self.ctx, embed_msg, self, self.challenger)

        self.view.msg = await self.ctx.send(embed=embed_msg, view=self.view)
        