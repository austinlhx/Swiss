class Card:
    def __init__(self, value, suit, emoji):
        self.value = value
        self.suit = suit
        self.emoji = emoji
        self.suit_name = self.__convert_suit()
        self.name = f"{self.__convert_rank()} of {self.suit_name}"
    
    def __convert_suit(self):
        suit_conversion = {0: "Diamonds", 1: "Clubs", 2: "Hearts", 3: "Spades"}
        return suit_conversion[self.suit]
    
    def __convert_rank(self):
        rank_conversion = {1: "Ace", 11: "Jack", 12: "Queen", 13: "King"}
        return rank_conversion.get(self.value, self.value)


    def __gt__(self, other):
        return self.value > other.value

    def __lt__(self, other):
        return self.value < other.value

    def __ge__(self, other):
        return self.value >= other.value

    def __le__(self, other):
        return self.value <= other.value

    def __eq__(self, other):
        return self.value == other.value

    def __ne__(self, other: object) -> bool:
        return self.value != other.value