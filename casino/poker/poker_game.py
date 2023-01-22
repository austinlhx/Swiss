from casino.deck.deck import CardDeck
from casino.poker.poker_player import Player
from casino.poker.poker_stages import PokerStage
from casino.poker.poker_logic import determine_winner

class PokerGame():
    def __init__(self, starting_player, small_blind_amount, big_blind_amount, buy_in):
        first_player = Player(starting_player, buy_in)
        self.players = [first_player]

        self.total_players = 1
        self.buy_in = buy_in

        self.deck = CardDeck()
        self.deck.shuffle()
        self.hidden_card = self.deck.hidden
        self.starting_player_index = 0

        self.small_blind_amount = small_blind_amount
        self.big_blind_amount = big_blind_amount 

        self.small_blind = None
        self.big_blind = None 

        self.current_player_index = 0
        # self.current_player = None
        self.current_check = 0
        self.current_total_pot = 0
        self.dealer_hand = []

        self.stage = PokerStage.PRE_FLOP
    
    def get_current_player(self):
        return self.players[self.current_player_index]
    
    def call_or_check(self):
        curr_player = self.players[self.current_player_index]
        if curr_player.current_game_bet == self.current_check:
            extra_bet_amount = 0
        else:
            extra_bet_amount = self.current_check - curr_player.current_game_bet
            #TODO: Have to deal with splttting pot issues
            if extra_bet_amount < 0:
                extra_bet_amount = curr_player.current_game_bet
        
        return extra_bet_amount
    
    def all_in(self):
        curr_player = self.players[self.current_player_index]
        total_credits = curr_player.get_credits()
        self.call(total_credits)
    
    def call(self, bet_amount):
        # Make sure they have enough money
        curr_player = self.players[self.current_player_index]

        #Could be a raise here
        if curr_player.current_game_bet + bet_amount > self.current_check:
            self.current_check = curr_player.current_game_bet + bet_amount

        curr_player.wager_credits(bet_amount)
        curr_player.check()
        self.current_total_pot += bet_amount

        if self.everyone_checks():
            winners = self.next_stage()
            if winners:
                return winners
            return True
        
        return False

        #Check to see if they are the last to call, then change the stage
    
    def next_stage(self):
        try:
            self.reset_checks()
            self.stage = PokerStage(self.stage.value + 1)
            if self.stage == PokerStage.FLOP:
                self.draw_flop()
            elif self.stage == PokerStage.RIVER or self.stage == PokerStage.TURN:
                self.draw_river_turn()
        except Exception:
            # exception should be index range
            return self.find_winner()
            #Game ended
        return False
    
    def find_winner(self):
        winners = determine_winner(self.players, self.dealer_hand)
        if len(winners) == 1:
            winning_player = winners[0]
            winning_player.increment_credits(self.current_total_pot)
        else:
            winning_credits = self.current_total_pot // len(winners)
            for winner in winners:
                winner.increment_credits(winning_credits)
                
        return winners

    def reset_checks(self):
        for player in self.players:
            player.uncheck()
    
    def everyone_checks(self):
        for player in self.players:
            if not player.folded and not player.checked:
                return False
        
        return True
    
    
    def raise_bet(self, credits_bet):
        curr_player = self.players[self.current_player_index]
        curr_player.wager_credits(credits_bet)
    
    def fold(self):
        curr_player = self.players[self.current_player_index]
        curr_player.folded = True

    def end_turn(self):
        finished_player = self.players[self.current_player_index]
        self.current_player_index = (self.current_player_index + 1) % self.total_players
        next_player = self.players[self.current_player_index]
        while next_player.folded:
            self.current_player_index = (self.current_player_index + 1) % self.total_players
            next_player = self.players[self.current_player_index]
            if next_player == finished_player:
                # End up at the same person, then everyone folded. 
                # Current player wins the pot
                next_player.increment_credits(self.current_total_pot)
                return self.reset_game()

    def start_new_game(self):
        self.wager_blinds()
        self.current_check = self.big_blind_amount
        self.current_total_pot = self.small_blind_amount + self.big_blind_amount
        for _ in range(2):
            for player in self.players:
                curr_card = self.deck.deck.pop(0)
                player.hand.append(curr_card)

    def draw_flop(self):
        self.deck.deck.pop(0) # Burn a card
        for _ in range(3):
            self.dealer_hand.append(self.deck.deck.pop(0))
    
    def draw_river_turn(self):
        self.deck.deck.pop(0) # Burn a card
        self.dealer_hand.append(self.deck.deck.pop(0))

    def add_player(self, player):
        new_player = Player(player, self.buy_in)
        self.players.append(new_player)
        self.total_players += 1

    def reset_game(self):
        # TODO: Pay players
        self.reset_players()
        self.dealer_hand = []

        self.deck = CardDeck()
        self.deck.shuffle()
        self.stage = PokerStage.PRE_FLOP
        self.starting_player_index = (self.starting_player_index + 1) % self.total_players
        self.current_player_index = self.starting_player_index

        self.wager_blinds()
        self.current_check = self.big_blind_amount
        self.current_total_pot = self.small_blind_amount + self.big_blind_amount

        for _ in range(2):
            for player in self.players:
                curr_card = self.deck.deck.pop(0)
                player.hand.append(curr_card)
    
    def reset_players(self):
        for player in self.players:
            player.reset_player()
    
    def wager_blinds(self):
        self.small_blind = self.players[self.starting_player_index]
        next_to_small = (self.starting_player_index + 1) % self.total_players
        self.big_blind = self.players[next_to_small]

        self.small_blind.wager_credits(self.small_blind_amount)
        self.big_blind.wager_credits(self.big_blind_amount)
        
        self.small_blind.set_small_blind()
        self.big_blind.set_big_blind()
    
