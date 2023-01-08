import discord, asyncio, logging
from discord.ui import Button, View

CACHE = {}

class BlackjackView(View):
    def __init__(self, ctx, embed, blackjack):
        super().__init__()
        self.ctx = ctx
        self.embed = embed
        self.blackjack = blackjack
    

    @discord.ui.button(label="Hit",style=discord.ButtonStyle.success)
    async def hit_command(self, interaction, button):
        await self.hit(interaction)
        if self.blackjack.doubled:
            await self.stand(interaction)


    @discord.ui.button(label="Stand",style=discord.ButtonStyle.danger)
    async def stand_command(self, interaction, button):
        await self.stand(interaction)
    

    @discord.ui.button(label="Double",style=discord.ButtonStyle.primary, custom_id="double")
    async def double_command(self, interaction, button):
        self.blackjack.doubled = True
        credits_available = await self.blackjack.wager_credits() 
        if not credits_available:
            self.blackjack.doubled = False
            return

        self.blackjack.credits *= 2
        
        await self.hit(interaction)


    async def hit(self, interaction):
        for child in self.children:
            if child.custom_id == "double":
                child.disabled = True
        new_card = self.blackjack.deck.deck.pop(0)
        self.blackjack.user_cards.append(new_card)
        card_names = [card.name for card in self.blackjack.user_cards]
        card_value = ', '.join(card_names)
        card_value += " | Total: " + str(self.blackjack.hand_total(self.blackjack.user_cards))
        self.embed.set_field_at(index=0, name="Your Hand", value= card_value)

        curr_total = self.blackjack.hand_total(self.blackjack.user_cards)

        if curr_total == 21:
            await self.stand(interaction)
        elif curr_total < 21:
            if self.blackjack.doubled:
                await self.stand(interaction)
            else:
                await interaction.response.edit_message(embed=self.embed, view=self)
        else:
            self.embed.add_field(name="Results", value="Player busts.", inline=False)
            await self.conclude_game(interaction)
    
    async def stand(self, interaction):
        curr_total = self.blackjack.hand_total(self.blackjack.dealer_cards)
        while curr_total <= 16:
            new_card = self.blackjack.deck.deck.pop(0)
            self.blackjack.dealer_cards.append(new_card)
            curr_total = self.blackjack.hand_total(self.blackjack.dealer_cards)

        card_names = [card.name for card in self.blackjack.dealer_cards]
        card_value = ', '.join(card_names)
        card_value += " | Total: " + str(self.blackjack.hand_total(self.blackjack.dealer_cards))
        self.embed.set_field_at(index=1, name="Dealer", value= card_value)

        user_total = self.blackjack.hand_total(self.blackjack.user_cards)

        if curr_total > 21 or (curr_total <= 21 and curr_total < user_total):
            await self.blackjack.double_credits()
            win_msg = "Player wins " + str(self.blackjack.credits)
            self.embed.add_field(name="Results", value=win_msg, inline=False)
        elif curr_total <= 21 and curr_total > user_total:
            self.embed.add_field(name="Results", value="Dealer wins.", inline=False)
        else:
            await self.blackjack.push_credits()
            self.embed.add_field(name="Results", value="Player pushes.", inline=False)

        await self.conclude_game(interaction)
    
    async def interaction_check(self, interaction):
        if self.ctx.author != interaction.user:
            await interaction.response.send_message("This is not your game, you fucking bitch!", ephemeral=True)
            return False
        elif not CACHE.get(self.ctx.author):
            await interaction.response.send_message("This game has already concluded.", ephemeral=True)
            return False
        
        return True
    
    async def on_error(self, interaction, error):
        logging.error("Error occured " + error + " from this " + interaction)
        del CACHE[self.ctx.author]
        await self.blackjack.push_credits()
        await interaction.response.send_message("Something weird happened, your credits have been returned. Please start a new game.", ephemeral=True)

    
    async def conclude_game(self, interaction):
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(embed=self.embed, view=self)
        
        del CACHE[self.ctx.author]

        _, user_credits = self.blackjack.extract_user()
        await self.ctx.send("You now have " + str(user_credits) + " credits.") 