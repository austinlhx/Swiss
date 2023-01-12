from discord.ui import View, button
from discord import ButtonStyle, Color

import asyncio, random

class RouletteView(View):
    def __init__(self, ctx, embed, roulette):
        super().__init__()
        self.ctx = ctx
        self.embed = embed
        self.roulette = roulette
        self.msg = None
        self.started = False
    
    @button(label="Red x2",style=ButtonStyle.danger)
    async def red(self, interaction, button):
        self.embed.set_field_at(index=1, name="Picked Color:", value="🔴", inline=False)
        await self.spin_wheel(interaction, "Red")
        
    @button(label="Black x2",style=ButtonStyle.gray)
    async def black(self, interaction, button):
        self.embed.set_field_at(index=1, name="Picked Color:", value="⚫", inline=False)
        await self.spin_wheel(interaction, "Black")
    
    @button(label="Green x14",style=ButtonStyle.success)
    async def green(self, interaction, button):
        self.embed.set_field_at(index=1, name="Picked Color:", value="🟢", inline=False)
        await self.spin_wheel(interaction, "Green")
    
    async def spin_wheel(self, interaction, color):
        self.started = True
        await interaction.response.edit_message(embed=self.embed, view=None)
        await self.spin_wheel_animation()
        self.ended = True
        winning_color = self.pick_random_color()
        if winning_color == "Green":
            self.embed.set_field_at(index=2, name="Landed Color: ", value="🟢", inline=False)
        elif winning_color == "Red":
            self.embed.set_field_at(index=2, name="Landed Color: ", value="🔴", inline=False)
        else:
            self.embed.set_field_at(index=2, name="Landed Color: ", value="⚫", inline=False)

        if winning_color == color:
            self.roulette.multiplied_credits(self.ctx.author.id, self.roulette.credits*2)
            self.embed.add_field(name="Results", value="Winner! You have won " + str(self.roulette.credits) + " credits.", inline=False)
            self.embed.color = Color.green()
            await self.msg.edit(embed=self.embed, view=None)
        else:
            self.embed.add_field(name="Results", value="Loser! You have lost " + str(self.roulette.credits) + " credits.", inline=False)
            self.embed.color = Color.red()
            await self.msg.edit(embed=self.embed, view=None)

    async def interaction_check(self, interaction):
        if self.ctx.author != interaction.user:
            await interaction.response.send_message("This is not your game!", ephemeral=True)
            return False
        
        return True

    async def spin_wheel_animation(self):
        count = 10
        while count >= 0:
            count -= 1
            await asyncio.sleep(1)
            if count % 5 == 0:
                self.embed.set_field_at(index=2, name="Current Color: ", value="🟢", inline=False)
            elif count % 2 == 0:
                self.embed.set_field_at(index=2, name="Current Color: ", value="⚫", inline=False)
            else:
                self.embed.set_field_at(index=2, name="Current Color: ", value="🔴", inline=False)

            await self.msg.edit(embed=self.embed, view=None)
    
    def pick_random_color(self):
        number = random.randint(1,15)
        if number == 15:
            return "Green"
        elif number > 7:
            return "Black"
        else:
            return "Red"
    
    async def on_error(self, interaction, error, item):
        await interaction.response.send_message("An error has occured! Please request another game.", ephemeral=True)
    
    async def on_timeout(self):
        if not self.started:
            self.roulette.multiplied_credits(self.ctx.author.id, self.roulette.credits)
            self.embed.add_field(name="Results", value="You took too long to respond. Your credits have been returned, please play again!", inline=False)
            self.embed.color = Color.yellow()
            await self.msg.edit(embed=self.embed, view=None)
    