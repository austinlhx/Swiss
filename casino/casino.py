import psycopg, os, logging

POSTGRES = os.environ["DATABASE_URL"]

class Casino():
    def __init__(self, credits, client, ctx):
        self.credits = credits
        self.client = client
        self.ctx = ctx
        self.view = None

    def extract_user_credits(self, user_id):
        with psycopg.connect(POSTGRES) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM credits WHERE user_id = %s",
                    (user_id,)
                )
                extracted_user = cur.fetchone()
            
                if not extracted_user:
                    return 0
                else:
                    return extracted_user[2]

    async def wager_credits(self, user_id):
        user_credits = self.extract_user_credits(user_id)

        if self.credits > user_credits:
            await self.ctx.send("You do not have sufficient credits, you have " + str(user_credits) + " credits.")  
            return False
        
        with psycopg.connect(POSTGRES) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE credits SET credit = credit - %s WHERE user_id = %s",
                    (self.credits, user_id)
                )

                if cur.rowcount == 0:
                    logging.warning("User wagered " + str(self.credits) + " but was not found in database.")
                    return

                conn.commit()
        
        return True

    
    def multiplied_credits(self, user_id, credits_won):
        with psycopg.connect(POSTGRES) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE credits SET credit = credit + %s WHERE user_id = %s",
                    (credits_won, user_id)
                )
                if cur.rowcount == 0:
                    logging.warning("User won " + str(credits_won) + " but was not found in database.")
                    return

                conn.commit()
                