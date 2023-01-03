from deck_of_cards import deck_of_cards

import json

CREDITS_FILE = 'credits.json'

class Blackjack():
    def __init__(self, credits, client, ctx): 
        self.credits = credits
        self.client = client
        self.ctx = ctx
        self.deck = deck_of_cards.DeckOfCards()
        self.deck.shuffle_deck()
        self.user_cards = []
        self.dealer_cards = []
        self.can_double = True
        self.doubled = False

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

        user_total = user_first_card_value + user_second_card_value
        hidden_card_value, up_card_value = self.card_value(hidden_card), self.card_value(up_card)

        if ((hidden_card_value == 1 and up_card_value + 11 == 21) or (up_card_value == 1 and hidden_card_value + 11 == 21)) and ((user_first_card_value == 1 and user_second_card_value + 11 == 21) or (user_second_card_value == 1 and user_first_card_value + 11 == 21)):
            await self.ctx.send("Both Players have Blackjack, Player pushes.")
            await self.push_credits()
            return True


        if(hidden_card_value == 1 and up_card_value + 11 == 21) or (up_card_value == 1 and hidden_card_value + 11 == 21):
            await self.ctx.send("Dealer has Blackjack")
            return True

        elif (user_first_card_value == 1 and user_second_card_value + 11 == 21) or (user_second_card_value == 1 and user_first_card_value + 11 == 21):
            await self.ctx.send("You have Blackjack, Congratulations!")
            await self.double_credits()
            return True
        
        await self.ctx.send("You have " + str(user_total))
        await self.ctx.send("Dealer shows a " + str(hidden_card_value))
        
        await self.ctx.send("Would you like to hit, stand, or double?")
        return False
    
    async def double_credits(self):
        user, _, data = self.retrieve_data_and_credits()
        credits_won = self.credits * 2
        data['credits'][user] += credits_won

        await self.update_credits(user, data)
    
    async def push_credits(self):
        user, _, data = self.retrieve_data_and_credits()
        credits_back = self.credits
        data['credits'][user] += credits_back

        await self.update_credits(user, data) 
    
    async def update_credits(self, user, data):
        with open(CREDITS_FILE, 'w') as json_file:
            json_data = json.dumps(data)
            json_file.write(json_data) 
            await self.ctx.send("You now have " + str(data['credits'][user]) + " credits.") 
    
    async def wager_credits(self):
        user, user_credits, data = self.retrieve_data_and_credits()
        if self.credits > user_credits:
            if self.doubled:
                await self.ctx.send("You do not have enough to double. You only have " + str(user_credits) + " credits remaining.")
            else:
                await self.ctx.send("You do not have sufficient credits, you have " + str(user_credits) + " credits.")  
            return False

        with open(CREDITS_FILE, 'w') as json_file:
            data['credits'][user] -= self.credits
            json_data = json.dumps(data)
            json_file.write(json_data)    
        
        return True
    
    def retrieve_data_and_credits(self):
        with open(CREDITS_FILE, 'r') as json_file:
            data = json.load(json_file)
            user = str(self.ctx.author.id)
            user_credits = data['credits'].get(user, 0)
        
        return user, user_credits, data  
    
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