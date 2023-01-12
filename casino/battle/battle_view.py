from discord.ui import View, button
from discord import ButtonStyle, Color

import asyncio, random

class BattleView(View):
    def __init__(self, ctx, embed, battle, challenger):
        super().__init__()
        self.ctx = ctx
        self.embed = embed
        self.battle = battle
        self.challenger = challenger
        self.msg = None
        self.ended = False
    
    @button(label="👍",style=ButtonStyle.success)
    async def accept(self, interaction, button):
        self.embed.add_field(name="Results: ", value="Player has accepted the game. Battle commences in 3 seconds.", inline=False)
        self.embed.color = Color.blue()
        self.embed.set_image(url=None)
        await interaction.response.edit_message(embed=self.embed, view=None)
        await self.battle.wager_credits(self.ctx.author.id)
        await self.battle.wager_credits(self.challenger.id)
        await self.randomize_player_animation()
        await self.pick_random_player()
        self.ended = True
        


    @button(label="👎",style=ButtonStyle.danger)
    async def decline(self, interaction, button):
        self.embed.add_field(name="Results: ", value="Player has declined the game", inline=False)
        self.embed.color = Color.yellow()
        await interaction.response.edit_message(embed=self.embed, view=None)
        self.ended = True
    

    async def interaction_check(self, interaction):
        if self.challenger != interaction.user:
            await interaction.response.send_message("This is not your game!", ephemeral=True)
            return False
        
        return True

    async def randomize_player_animation(self):
        await asyncio.sleep(3)
        count = 10
        self.embed.set_image(url="https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/CENSORED.svg/1280px-CENSORED.svg.png")
        await self.msg.edit(embed=self.embed, view=None)
        while count >= 0:
            count -= 1
            await asyncio.sleep(0.5)
            if count % 2 == 0:
                self.embed.set_field_at(index=1, name="Current Winner:", value= self.ctx.author.name, inline=False)
            else:
                self.embed.set_field_at(index=1, name="Current Winner:", value= self.challenger.name, inline=False)
            self.embed.set_field_at(index=2, name="Results", value= "The fight is happening!", inline=False)
            await self.msg.edit(embed=self.embed, view=None)
    
    async def pick_random_player(self):
        number = random.randint(1,2)
        if number == 1:
            self.battle.multiplied_credits(self.ctx.author.id, self.battle.credits*2)
            self.embed.set_image(url="https://media.tenor.com/hyWuotawRqUAAAAC/jango-head.gif")
            winner_str = "Successful swing! The challenger managed to have a clean swing and cuts " + self.challenger.name + "'s head off."
            self.embed.set_field_at(index=1, name="State", value= winner_str, inline=False)
            self.embed.set_field_at(index=2, name="Results", value=self.ctx.author.name + " wins " + str(self.battle.credits) + " credits!", inline=False)
            self.embed.color = Color.green()
        else:
            self.battle.multiplied_credits(self.challenger.id, self.battle.credits*2)
            self.embed.set_image(url="https://media.tenor.com/QPPUJ9ouw6QAAAAC/defeated.gif")
            winner_str = "Unsuccessful swing! " + self.challenger.name + " strikes back."
            self.embed.set_field_at(index=1, name="State", value= winner_str, inline=False)
            self.embed.set_field_at(index=2, name="Results", value=self.challenger.name + " wins " + str(self.battle.credits) + " credits!", inline=False)
            self.embed.color = Color.red()
        await self.msg.edit(embed=self.embed, view=None)
    
    async def on_error(self, interaction, error, item):
        await interaction.response.send_message("An error has occured! Please request another game.", ephemeral=True)
    
    async def on_timeout(self):
        if not self.ended:
            self.embed.set_field_at(index=1, name="Results", value=self.challenger.name + " took too long to respond. This game has been concluded.", inline=False)
            self.embed.color = Color.yellow()
            await self.msg.edit(embed=self.embed, view=None)
    