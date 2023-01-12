from discord.ui import View, button
from discord import ButtonStyle, Color

import random

class RPSChoices(View):
    def __init__(self, ctx, embed, rps, challenger, msg):
        super().__init__()
        self.ctx = ctx
        self.embed = embed
        self.rps = rps
        self.challenger = challenger
        self.player_one = None
        self.player_two = None
        self.msg = msg
        self.ended = False
    

    @button(label="👊",style=ButtonStyle.success)
    async def rock(self, interaction, button):
        if interaction.user == self.ctx.author:
            self.player_one = "Rock"
        elif interaction.user == self.challenger:
            self.player_two = "Rock"
        await interaction.response.send_message("You have picked rock!", ephemeral=True)

        if self.player_one and self.player_two:
            await self.determine_outcome()
        
    @button(label="✋",style=ButtonStyle.danger)
    async def paper(self, interaction, button):
        if interaction.user == self.ctx.author:
            self.player_one = "Paper"
        elif interaction.user == self.challenger:
            self.player_two = "Paper"
        await interaction.response.send_message("You have picked paper!", ephemeral=True)

        if self.player_one and self.player_two:
            await self.determine_outcome()
    
    @button(label="✌️",style=ButtonStyle.primary)
    async def scissors(self, interaction, button):
        if interaction.user == self.ctx.author:
            self.player_one = "Scissors"
        elif interaction.user == self.challenger:
            self.player_two = "Scissors"
        await interaction.response.send_message("You have picked scissors!", ephemeral=True)

        if self.player_one and self.player_two:
            await self.determine_outcome()
    
    async def determine_outcome(self):
        self.embed.set_field_at(index=1, name="Player", value=self.player_one, inline=True)
        self.embed.set_field_at(index=2, name="Challenger", value=self.player_two, inline=True)

        if self.player_one == self.player_two:
            await self.tie()
        elif self.player_one == "Rock":
            if self.player_two == "Paper":
                await self.player_two_win()
            else:
                await self.player_one_win()
        elif self.player_one == "Paper":
            if self.player_two == "Rock":
                await self.player_one_win()
            else:
                await self.player_two_win()
        else:
            if self.player_two == "Rock":
                await self.player_two_win()
            else:
                await self.player_one_win()
        self.ended = True
    
    async def player_one_win(self):
        self.rps.multiplied_credits(self.ctx.author.id, self.rps.credits*2)
        self.embed.add_field(name="Results", value="Player wins!", inline=False)
        self.embed.color = Color.green()
        await self.msg.edit(embed=self.embed, view=None)

    async def player_two_win(self):
        self.rps.multiplied_credits(self.challenger.id, self.rps.credits*2)
        self.embed.add_field(name="Results", value="Challenger wins!", inline=False)
        self.embed.color = Color.red()
        await self.msg.edit(embed=self.embed, view=None)

    async def tie(self):
        self.rps.multiplied_credits(self.ctx.author.id, self.rps.credits)
        self.rps.multiplied_credits(self.challenger.id, self.rps.credits)
        self.embed.add_field(name="Results", value="Tied!", inline=False)
        self.embed.color = Color.yellow()
        await self.msg.edit(embed=self.embed, view=None)

    async def on_timeout(self):
        if not self.player_one:
            random_pick = random.randint(1,3)
            if random_pick == 1:
                self.player_one = "Rock"
            elif random_pick == 2:
                self.player_one = "Paper"
            else:
                self.player_one = "Scissors"
        if not self.player_two:
            random_pick = random.randint(1,3)
            if random_pick == 1:
                self.player_two = "Rock"
            elif random_pick == 2:
                self.player_two = "Paper"
            else:
                self.player_two = "Scissors"
        if not self.ended:
            await self.determine_outcome()
    
    async def interaction_check(self, interaction):
        if self.challenger != interaction.user and self.ctx.author != interaction.user:
            await interaction.response.send_message("This is not your game!", ephemeral=True)
            return False
        
        if (self.player_one and self.ctx.author == interaction.user) or (self.player_two and self.challenger == interaction.user):
            await interaction.response.send_message("You have already chosen!", ephemeral=True)
            return False

        return True
