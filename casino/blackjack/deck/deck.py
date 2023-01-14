from casino.blackjack.deck.card import Card
from casino.blackjack.deck.emoji import CARD_EMOJIS

import random

class CardDeck:
    def __init__(self):
        self.deck = self.__generate_deck()
        self.hidden = CARD_EMOJIS[52]

    def shuffle(self):
        random.shuffle(self.deck)

    def __generate_deck(self):
        deck = []
        emoji_index = 0
        for value in range(1, 14):
            for suit in range(4): 
                curr_card = Card(value, suit, CARD_EMOJIS[emoji_index])
                deck.append(curr_card)
                emoji_index += 1
        
        return deck