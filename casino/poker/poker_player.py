class Player():
    def __init__(self, player_info, credits):
        self.player_info = player_info
        self.credits = credits
        self.current_game_bet = 0
        self.hand = []
        self.folded = False
        self.checked = False
        self.blind_status = None

    def set_big_blind(self):
        self.blind_status = "Big"
    
    def set_small_blind(self):
        self.blind_status = "Small"
    
    def check(self):
        self.checked = True
    
    def uncheck(self):
        self.checked = False
    
    def get_credits(self):
        return self.credits
    
    def wager_credits(self, credits):
        #TODO: Check to make sure player has enough credits
        self.current_game_bet += credits
        self.credits -= credits
    
    def increment_credits(self, credits):
        self.credits += credits
    
    def reset_player(self):
        self.current_game_bet = 0
        self.folded = False
        self.hand = []
        self.blind_status = None
    
    def get_name(self):
        return self.player_info.name
    
    def get_mention(self):
        return self.player_info.mention