from discord.ui import Modal, TextInput


class RaiseModal(Modal):
    def __init__(self, choice_view):
        super().__init__(title="Raise")
        self.choice_view = choice_view
        raise_value = TextInput(label="Amount")
        self.add_item(raise_value)
    

    async def on_submit(self, interaction):
        curr_player = self.choice_view.poker.players[self.choice_view.poker.current_player_index].player_info
        current_bet = self.choice_view.poker.call_or_check()
        try:
            raise_value = interaction.data['components'][0]['components'][0]['value']
            raise_amount = int(raise_value)
        except Exception:
            return await interaction.response.send_message("Please enter a number!")
        if raise_amount < 10 + current_bet:
            return await interaction.response.send_message("Please raise a value higher than " + str(current_bet + 10) + "!")
        bet_amount = raise_amount - current_bet
        stage_change = self.choice_view.poker.call(bet_amount)
        self.choice_view.update_curr_player_table()
        self.choice_view.poker.end_turn()
        last_action = curr_player.name + " raises " + str(bet_amount)

        next_player_check_or_bet = self.choice_view.poker.call_or_check()
        self.choice_view.update_check_button(next_player_check_or_bet)

        if stage_change:
            self.choice_view.update_dealer_cards()

        self.choice_view.update_mention_player()
        self.choice_view.update_total_pot()
        self.choice_view.update_last_action(last_action)
        
        await interaction.response.edit_message(embed=self.choice_view.embed, view=self.choice_view)
        


