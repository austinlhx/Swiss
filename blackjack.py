from deck_of_cards import deck_of_cards

import json, os, psycopg, logging

POSTGRES = os.environ["DATABASE_URL"]
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
        user_id = self.ctx.author.id

        with psycopg.connect(POSTGRES) as conn:
            with conn.cursor() as cur:
                credits_won = self.credits * 2
                cur.execute(
                    "UPDATE credits SET credit = credit + %s WHERE user_id = %s",
                    (credits_won, user_id)
                )
                if cur.rowcount == 0:
                    logging.warning("User won " + str(self.credits * 2) + " but was not found in database.")
                    return

                conn.commit()
        
        await self.send_credit_updates() 
    
    async def push_credits(self):
        user = self.ctx.author.id

        with psycopg.connect(POSTGRES) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE credits SET credit = credit + %s WHERE user_id = %s",
                    (self.credits, user)
                )
                if cur.rowcount == 0:
                    logging.warning("User won " + str(self.credits) + " but was not found in database.")
                    return

                conn.commit()

        await self.send_credit_updates() 
    
    async def wager_credits(self):
        user, user_credits = self.extract_user()
        if self.credits > user_credits:
            if self.doubled:
                await self.ctx.send("You do not have enough to double. You only have " + str(user_credits) + " credits remaining.")
            else:
                await self.ctx.send("You do not have sufficient credits, you have " + str(user_credits) + " credits.")  
            return False
        
        with psycopg.connect(POSTGRES) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE credits SET credit = credit - %s WHERE user_id = %s",
                    (self.credits, user)
                )

                if cur.rowcount == 0:
                    logging.warning("User wagered " + str(self.credits) + " but was not found in database.")
                    return

                conn.commit()
        
        return True
    
    async def send_credit_updates(self):
        _, user_credits = self.extract_user()
        await self.ctx.send("You now have " + str(user_credits) + " credits.") 
    
    def extract_user(self):
        user = self.ctx.author.id
        
        with psycopg.connect(POSTGRES) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM credits WHERE user_id = %s",
                    (user,)
                )
                extracted_user = cur.fetchone()
            
                if not extracted_user:
                    return user, 0
                else:
                    return user, extracted_user[2]
    
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