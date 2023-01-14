import discord, logging
from discord.ui import Button, View

class CrashView(View):
    def __init__(self, ctx, embed, crash):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.embed = embed
        self.crash = crash
    

    @discord.ui.button(label="Cash Out",style=discord.ButtonStyle.success)
    async def cashout_command(self, interaction, button):
        self.crash.cashed_out = True
        credits_won = int(self.crash.credits * self.crash.current_multiplier)
        self.embed.add_field(name="Results: ", value= "Cashed Out! Won: " + str(credits_won) + " credits", inline=False)
        self.embed.color = discord.Color.green()
        await interaction.response.edit_message(embed=self.embed, view=None)
    
    async def interaction_check(self, interaction):
        if self.ctx.author != interaction.user:
            await interaction.response.send_message("This is not your game!", ephemeral=True)
            return False
        
        return True

    async def on_error(self, interaction, error, item):
        logging.error("Error occured " + str(error) + " from this " + str(interaction))
        self.crash.multiplied_credits(self.ctx.author.id, self.crash.credits)
        await interaction.response.send_message("Something weird happened, your credits have been returned. Please start a new game.", ephemeral=True)