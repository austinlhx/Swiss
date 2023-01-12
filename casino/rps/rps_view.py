from discord.ui import View, button
from discord import ButtonStyle, Color, Embed
from casino.rps.rps_choices import RPSChoices

import asyncio, random

class RPSView(View):
    def __init__(self, ctx, embed, rps, challenger):
        super().__init__()
        self.ctx = ctx
        self.embed = embed
        self.rps = rps
        self.challenger = challenger
        self.msg = None
        self.ended = False
    
    @button(emoji="👍",style=ButtonStyle.success)
    async def accept(self, interaction, button):
        self.embed.add_field(name="Results: ", value="Player has accepted the game. RPS commences in 3 seconds.", inline=False)
        self.embed.color = Color.blue()
        self.embed.set_image(url=None)
        await interaction.response.edit_message(embed=self.embed, view=None)
        await self.rps.wager_credits(self.ctx.author.id)
        await self.rps.wager_credits(self.challenger.id)
        await asyncio.sleep(3)
        await self.display_options()
        self.ended = True

    @button(label="👎",style=ButtonStyle.danger)
    async def decline(self, interaction, button):
        self.embed.add_field(name="Results: ", value="Player has declined the game", inline=False)
        self.embed.color = Color.yellow()
        await interaction.response.edit_message(embed=self.embed, view=None)
    

    async def interaction_check(self, interaction):
        if self.challenger != interaction.user:
            await interaction.response.send_message("This is not your game!", ephemeral=True)
            return False
        
        return True

    async def display_options(self):
        options = RPSChoices(self.ctx, self.embed, self.rps, self.challenger, self.msg)
        self.embed.set_field_at(index=1, name="State", value="Game has started! Awaiting user choices.", inline=False)
        self.embed.set_field_at(index=2, name="Player", value="Picking...", inline=True)
        self.embed.add_field(name="Challenger", value="Picking...", inline=True)
        await self.msg.edit(embed=self.embed, view=options)
    
    async def on_error(self, interaction, error, item):
        await interaction.response.send_message("An error has occured! Please request another game.", ephemeral=True)
    
    async def on_timeout(self):
        if not self.ended:
            self.embed.set_field_at(index=1, name="Results", value=self.challenger.name + " took too long to respond. This game has been concluded.", inline=False)
            self.embed.color = Color.yellow()
            await self.msg.edit(embed=self.embed, view=None)
    