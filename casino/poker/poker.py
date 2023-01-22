from casino.casino import Casino
from casino.poker.poker_view import PokerView
from casino.poker.poker_game import PokerGame
from discord import Embed, Color

class Poker(Casino):
    def __init__(self, small_blind, client, buy_in, leader, ctx):
        super().__init__(buy_in, client, ctx)
        self.view = None
        self.msg = None
        self.starting_player = leader
        self.small_blind_amount = small_blind
        self.big_blind_amount = small_blind * 2
        
    async def start_game(self):
        embed_msg = Embed(title="Poker", color=Color.blue())
        embed_msg.set_author(name=self.ctx.author.name, icon_url=self.ctx.author.display_avatar)
        embed_msg.add_field(name="Buy-in:", value=str(self.credits) + " credits", inline=False)
        embed_msg.add_field(name="Blinds", value=str(self.small_blind_amount) + "/" + str(self.big_blind_amount) + " credits", inline=False)

        player_str = "Balance: " + str(self.credits) + "\n" + "Current Bet: None" + "\n" + "Status: None"

        embed_msg.add_field(name=self.ctx.author.name, value=player_str, inline=True)
        embed_msg.add_field(name="State", value="Awaiting players...", inline=False)
        new_poker_game = PokerGame(self.starting_player, self.small_blind_amount, self.big_blind_amount, self.credits)
        self.view = PokerView(self.ctx, embed_msg, new_poker_game, self)
        self.view.msg = await self.ctx.send(embed=embed_msg, view=self.view)