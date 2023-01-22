from discord.ui import View, button
from discord import ButtonStyle, Color, Embed
from casino.poker.poker_choices import PokerChoices



class PokerView(View):
    def __init__(self, ctx, embed, poker, casino):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.embed = embed
        self.poker = poker
        self.casino = casino
        self.msg = None
        self.ended = False
        self.poker_choice_view = None
        self.current_player_table_index = 2
        
    
    @button(label="Join",style=ButtonStyle.success)
    async def join(self, interaction, button):
        joining_user = interaction.user
        #TODO: Commented for testing purposes
        if joining_user in self.poker.players:
            return await interaction.response.send_message("You have already joined the game!", ephemeral=True)
        credits_available = self.poker.extract_user_credits(joining_user.id)
        if credits_available < self.poker.buy_in:
            return await interaction.response.send_message("You do not have enough credits to join!")
        
        self.poker.add_player(joining_user)
        self.current_player_table_index += 1

        player_str = self.generate_player_table(self.poker.buy_in, None, None, None)
        self.embed.insert_field_at(index=self.current_player_table_index, name=joining_user.name,value=player_str, inline=True)


        await interaction.response.edit_message(embed=self.embed, view=self)

    @button(label="Start Game",style=ButtonStyle.danger)
    async def start(self, interaction, button):
        if len(self.poker.players) < 2:
            return await interaction.response.send_message("This game needs at least 3 players to start!")

        for player in self.poker.players:
            await self.casino.wager_credits(player.player_info.id)

        self.poker.start_new_game()
        # self.poker.current_player_view_index = 2
        await self.display_options(interaction)
        

    async def interaction_check(self, interaction):
        return True
    #TODO: Use caching

    #Calculation = player_num % (player_count + 2) +
    async def display_options(self, interaction):     
        small_blind_str = self.generate_player_table(self.poker.small_blind.credits, self.poker.small_blind.current_game_bet, None, "Small Blind")
        big_blind_str = self.generate_player_table(self.poker.big_blind.credits, self.poker.big_blind.current_game_bet, None, "Big Blind")

        self.embed.set_field_at(index=2, name=self.poker.players[0].get_name(), value=small_blind_str)
        self.embed.set_field_at(index=3, name=self.poker.players[1].get_name(), value=big_blind_str)
            
        self.poker_choice_view = PokerChoices(self.ctx, self.embed, self.poker, self.msg)
        self.embed.set_field_at(index=self.current_player_table_index + 1, name="Cards", value=self.poker.deck.hidden, inline=False)

        self.embed.add_field(name= "Total Pot", value=(self.poker.current_total_pot))
        self.embed.add_field(name="Current Turn", value=self.poker.get_current_player().get_mention())
        self.embed.add_field(name="Last Action", value=None)
        await self.edit_button_labels()
        await interaction.response.edit_message(embed=self.embed, view=self.poker_choice_view)
    
    async def edit_button_labels(self):
        for button in self.poker_choice_view.children:
            if button.custom_id == "check":
                button.label = "Call (" + str(self.poker.current_check - self.poker.small_blind_amount) + ")"
            if button.custom_id == "raise":
                button.label = "Raise"

    
    async def on_error(self, interaction, error, item):
        print(error)
        await interaction.response.send_message("An error has occured! Please request another game.", ephemeral=True)
    
    async def on_timeout(self):
        pass
        # if not self.ended:
        #     self.embed.set_field_at(index=1, name="Results", value=self.challenger.name + " took too long to respond. This game has been concluded.", inline=False)
        #     self.embed.color = Color.yellow()
        #     await self.msg.edit(embed=self.embed, view=None)
    
    def generate_player_table(self, balance, bet, status, blind):
        if not bet:
            bet = "None"
        if not status:
            status = "None"
        if not blind:
            blind = "None"
        
        cards = self.poker.hidden_card + " " + self.poker.hidden_card + "\n"
        player_table = cards +  "Balance: " + str(balance) + "\n" + "Current Bet: " + str(bet) + "\n" + "Status: " + status + "\n" + "Blind: " + blind

        return player_table
    

