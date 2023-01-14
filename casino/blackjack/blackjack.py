from deck_of_cards import deck_of_cards
from casino.casino import Casino
from casino.blackjack.deck.deck import CardDeck

import os, logging, discord, asyncio
from casino.blackjack.blackjack_view import BlackjackView

POSTGRES = os.environ["DATABASE_URL"]

class Blackjack(Casino):
    def __init__(self, credits, client, ctx): 
        super().__init__(credits, client, ctx)
        self.deck = CardDeck()
        self.deck.shuffle()
        self.user_cards = []
        self.dealer_cards = []
        self.can_double = True
        self.doubled = False
        self.view = None

    async def start_game(self):
        user_first_card = self.deck.deck.pop(0)
        hidden_card = self.deck.deck.pop(0)
        user_second_card = self.deck.deck.pop(0)
        up_card = self.deck.deck.pop(0)

        self.user_cards.append(user_first_card)
        self.user_cards.append(user_second_card)

        self.dealer_cards.append(hidden_card)
        self.dealer_cards.append(up_card)

        user_first_card_value, user_second_card_value = self.card_value(user_first_card), self.card_value(user_second_card)

        hidden_card_value, up_card_value = self.card_value(hidden_card), self.card_value(up_card)

        if ((hidden_card_value == 1 and up_card_value + 11 == 21) or (up_card_value == 1 and hidden_card_value + 11 == 21)) and ((user_first_card_value == 1 and user_second_card_value + 11 == 21) or (user_second_card_value == 1 and user_first_card_value + 11 == 21)):
            await self.ctx.send("Both Players have Blackjack, Player pushes.")
            self.multiplied_credits(self.ctx.author.id, self.credits)
            return True


        if(hidden_card_value == 1 and up_card_value + 11 == 21) or (up_card_value == 1 and hidden_card_value + 11 == 21):
            await self.ctx.send("Dealer has Blackjack")
            return True

        elif (user_first_card_value == 1 and user_second_card_value + 11 == 21) or (user_second_card_value == 1 and user_first_card_value + 11 == 21):
            await self.ctx.send("You have Blackjack, Congratulations!")
            credits_won = self.credits*2
            self.multiplied_credits(self.ctx.author.id, credits_won)
            return True
        
        user_hand = [card.emoji for card in self.user_cards]
        user_hand_str = ' '.join(user_hand)
        user_hand_str += " | Total: " + str(self.hand_total(self.user_cards))

        dealer_hand_str = self.deck.hidden + " " + up_card.emoji + " | Total: " + str(up_card_value)
        embed_message = discord.Embed(title="Blackjack")
        embed_message.set_author(name=self.ctx.author.name, icon_url=self.ctx.author.display_avatar)
        embed_message.add_field(name="Your Hand", value=user_hand_str, inline=False)
        embed_message.add_field(name="Dealer", value=dealer_hand_str, inline=False)
        embed_message.color = discord.Color.blue()
        self.view = BlackjackView(self.ctx, embed_message, self)
        self.view.msg = await self.ctx.send(embed=embed_message, view= self.view)
        return False
    
    def draw_cards(self):
        pass
    
    def hand_total(self, hand):
        curr_total = 0
        ace_included = False
        for card in hand:
            card_val = self.card_value(card)
            curr_total += card_val
            if card_val == 1:
                ace_included = True

        if ace_included and curr_total <= 11:
            curr_total += 10
        
        return curr_total
        
    def card_value(self, card):
        if card.value == 11 or card.value == 12 or card.value == 13:
            return 10
        else:
            return card.value