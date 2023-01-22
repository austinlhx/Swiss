from discord.ui import View, button, Modal, TextInput
from discord import ButtonStyle, Color, Embed
from casino.poker.poker_stages import PokerStage
from casino.poker.poker_raise import RaiseModal
from casino.deck.deck import CardDeck

import random, logging, asyncio

class PokerChoices(View):
    def __init__(self, ctx, embed, poker, msg):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.embed = embed
        self.poker = poker
        self.msg = msg
        self.ended = False
        self.stage = PokerStage.PRE_FLOP
    
    def get_mention_index(self):
        return self.poker.total_players + 2 + 2
    
    def get_dealer_card_index(self):
        return self.poker.total_players + 2

    def get_total_pot_index(self):
        return self.poker.total_players + 3
    
    def get_last_turn_index(self):
        return self.poker.total_players + 5

    def get_current_player_view_index(self):
        return self.poker.current_player_index + 2

    @button(label="Check",style=ButtonStyle.success, custom_id="check")
    async def check(self, interaction, button):
        curr_player = self.poker.players[self.poker.current_player_index].player_info

        if interaction.user != curr_player:
            return await interaction.response.send_message("It is not your turn!", ephemeral=True)

        current_bet = self.poker.call_or_check()

        stage_change = self.poker.call(current_bet)
        self.update_curr_player_table()
        self.poker.end_turn()

        if current_bet == 0:
            last_action = curr_player.name + " calls."
        else:
            last_action = curr_player.name + " checks."

        next_player_check_or_bet = self.poker.call_or_check()

        self.update_check_button(next_player_check_or_bet)

        if stage_change == True:
            self.update_dealer_cards()
        elif stage_change:
            winners = stage_change
            if len(winners) == 1:
                winning_str = winners[0].player_info.name + " wins " + str(self.poker.current_total_pot) + "!"
            else:
                winning_names = [winner.player_info.name for winner in winners]
                winning_str = ', '.join(winning_names) + " split the pot of " + str(self.poker.current_total_pot) + "!"
            last_action = winning_str
            self.update_last_action(last_action)
            self.reveal_all_player_cards()
            
            await interaction.response.edit_message(embed=self.embed, view=self)

            await asyncio.sleep(5)

            return await self.reset_game(interaction)
            # self.reset_game()



        self.update_mention_player()
        self.update_total_pot()
        self.update_last_action(last_action)
        
        await interaction.response.edit_message(embed=self.embed, view=self)
    
    #TODO: If everyone all_ins just run it down the flops

    
    async def reset_game(self, interaction):
        self.poker.reset_game()
        self.update_all_players()
        self.update_dealer_cards()
        self.update_mention_player()
        self.update_total_pot()
        next_player_check_or_bet = self.poker.call_or_check()
        self.update_check_button(next_player_check_or_bet)

        await self.msg.edit(embed=self.embed, view=self)


    def update_check_button(self, next_player_check_or_bet):
        if next_player_check_or_bet != 0: #need to udpate label for NEXT player
            for button in self.children:
                if button.custom_id == "check":
                    button.label = "Call (" + str(next_player_check_or_bet) + ")"
        else:
            for button in self.children:
                if button.custom_id == "check":
                    button.label = "Check"
    
    def update_total_pot(self):
        total_pot = self.poker.current_total_pot
        self.embed.set_field_at(index=self.get_total_pot_index(), name="Total Pot", value=total_pot)
    
    def update_last_action(self, action):
        self.embed.set_field_at(index=self.get_last_turn_index(), name="Last Action", value=action, inline=False)
    
    def update_mention_player(self):
        curr_player = self.poker.get_current_player()
        mention_player = curr_player.get_mention()
        self.embed.set_field_at(index=self.get_mention_index(), name="Current Turn", value=mention_player)
    
    def update_all_players(self):
        starting_view_index = 2
        for curr_player in self.poker.players:
            player_str = self.generate_player_table(curr_player.credits, curr_player.current_game_bet, curr_player.folded, curr_player.blind_status)
            self.embed.set_field_at(index=starting_view_index, name=curr_player.get_name(), value=player_str)
            starting_view_index += 1

    def reveal_all_player_cards(self):
        starting_view_index = 2
        for curr_player in self.poker.players:
            player_str = self.generate_player_cards_table(curr_player, curr_player.credits, curr_player.current_game_bet, curr_player.folded, curr_player.blind_status)
            self.embed.set_field_at(index=starting_view_index, name=curr_player.get_name(), value=player_str)
            starting_view_index += 1
    
    def update_curr_player_table(self):
        curr_player = self.poker.get_current_player()
        player_str = self.generate_player_table(curr_player.credits, curr_player.current_game_bet, curr_player.folded, curr_player.blind_status)
        view_index = self.get_current_player_view_index()
        self.embed.set_field_at(index=view_index, name=curr_player.get_name(), value=player_str)
    
    
    @button(label="Raise",style=ButtonStyle.secondary, custom_id="raise")
    async def raise_button(self, interaction, button):
        curr_player = self.poker.get_current_player().player_info

        if interaction.user != curr_player:
            return await interaction.response.send_message("It is not your turn!", ephemeral=True)
        modal = RaiseModal(self)
        await interaction.response.send_modal(modal)


    #TODO
    @button(label="All in",style=ButtonStyle.danger, custom_id="all_in")
    async def all_in(self, interaction, button):
        curr_player = self.poker.get_current_player().player_info

        if interaction.user != curr_player:
            return await interaction.response.send_message("It is not your turn!", ephemeral=True)

        self.poker.all_in()
        self.update_curr_player_table()
        self.poker.end_turn()
        last_action = curr_player.name + " all ins."

        next_player_check_or_bet = self.poker.call_or_check()

        self.update_check_button(next_player_check_or_bet)
        self.update_mention_player()
        self.update_total_pot()
        self.update_last_action(last_action)
        
        await interaction.response.edit_message(embed=self.embed, view=self)

    
    @button(label="Fold",style=ButtonStyle.danger)
    async def fold(self, interaction, button):
        curr_player = self.poker.get_current_player().player_info

        if interaction.user != curr_player:
            return await interaction.response.send_message("It is not your turn!", ephemeral=True)

        self.poker.fold()
        self.update_curr_player_table()
        self.poker.end_turn()

        next_player_check_or_bet = self.poker.call_or_check()

        self.update_check_button(next_player_check_or_bet)

        self.update_mention_player()
        last_action = curr_player.name + " folds."
        self.update_last_action(last_action)

        await interaction.response.edit_message(embed=self.embed, view=self)

    
    @button(label="View Cards",style=ButtonStyle.primary)
    async def view_cards(self, interaction, button):
        curr_user = interaction.user
        for player in self.poker.players:
            if player.player_info == curr_user:
                cards = player.hand
                #TODO: Handle if a player tries to view card and they not in the game.
                break
  
        card_emoji = [card.emoji for card in cards]
        card_embed = Embed(title="Your cards", description=' '.join(card_emoji))
        await interaction.response.send_message(embed=card_embed, ephemeral=True)

    async def on_timeout(self):
        pass
    
    async def interaction_check(self, interaction):
        return True
    

    # async def on_error(self, interaction, error, item):
    #     logging.error("Error occured " + str(error) + " from this " + str(interaction))
    #     await interaction.response.send_message("Something weird happened, your error has been logged. Please start a new game.", ephemeral=True)
    
    def update_dealer_cards(self):
        card_emojis = [card.emoji for card in self.poker.dealer_hand]
        card_value = ' '.join(card_emojis)
        self.embed.set_field_at(index=self.get_dealer_card_index(), name="Cards", value=card_value, inline=False)

    def generate_player_table(self, balance, bet, status, blind):

        if not bet:
            bet = "None"
        if not status:
            status = "None"
        else:
            status = "Folded"
        if not blind:
            blind = "None"
        cards = self.poker.hidden_card + " " + self.poker.hidden_card + "\n"
        player_table = cards + "Balance: " + str(balance) + "\n" + "Current Bet: " + str(bet) + "\n" + "Status: " + status + "\n" + "Blind: " + blind

        return player_table
    
    def generate_player_cards_table(self, player, balance, bet, status, blind):
        # If they folded, do not reveal their cards
        if not bet:
            bet = "None"
        if not status:
            status = "None"
            cards = player.hand[0].emoji + " " + player.hand[1].emoji + "\n"
        else:
            status = "Folded"
            cards = self.poker.hidden_card + " " + self.poker.hidden_card + "\n"
        if not blind:
            blind = "None"

        player_table = cards + "Balance: " + str(balance) + "\n" + "Current Bet: " + str(bet) + "\n" + "Status: " + status + "\n" + "Blind: " + blind

        return player_table
