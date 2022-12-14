class BetaGammaBot():
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.reactions = True
        client = discord.Client(intents=intents)