import os
from openai import OpenAI

from dotenv import load_dotenv
import toml
from pathlib import Path

load_dotenv()

PROMPT_TEMPLATE = """
You are a Player in an investment game.
Player A has sent you {amount_to_send} currency units, which was proliferated to {received_amount} through investment.
Added to your previous asset, you now have {player_b_balance} currency units.
You have decided to return {amount_to_return} to the Player A.
Assuming you are a person with the personality characterized by [description], 
write a short message to justify this transaction.
"""

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)


def generate_response(
    *,
    profile: dict,
    amount_to_send: int,
    received_amount: int,
    player_b_balance: int,
    amount_to_return: int,
) -> str:
    instructions = """
   You are Player B and in an investment game with Player A. 
   After the transaction, you need to send a one-sentence message to Player A. 
   The message should reflect the player's personality or investment strategy as much as possible, 
   and should be no more than 100 characters written in Korean.
    """

    description = profile["description"]
    prompt = PROMPT_TEMPLATE.format(
        amount_to_send=amount_to_send,
        received_amount=received_amount,
        player_b_balance=player_b_balance,
        amount_to_return=amount_to_return,
        description=description,
    )

    response = client.responses.create(
        model="gpt-4.1-nano",
        instructions=instructions,
        input=prompt,
    )

    return response.output_text


if __name__ == "__main__":
    PROFILES_PATH: Path = Path(__file__).parent / "profiles" / "personalities.toml"
    with open(PROFILES_PATH, "r") as f:
        PERSONALITY_PROFILES = toml.load(f)
    profile = PERSONALITY_PROFILES["penny-pincher"]
    print(
        generate_response(
            profile=profile,
            amount_to_send=5,
            received_amount=15,
            player_b_balance=25,
            amount_to_return=7,
        )
    )
