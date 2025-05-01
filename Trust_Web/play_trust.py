# https://claude.ai/chat/f2799484-a7f2-4bf1-87f2-33bdd544b14b
import datetime
import json
from pathlib import Path
import numpy as np
import random
from pydantic import BaseModel, Field
from openai import OpenAI
import toml

PROLIFERATION_FACTOR = 2
INITIAL_BALANCE = 20
NUM_ROUNDS = 7


class Response(BaseModel):
    amount_returned: int = Field(description="The amount returned to the human player.")
    message: str = Field(description="A brief message explaining the decision.")


class PlayRequest(BaseModel):
    amount_sent: int


def ensure_directory_exists(directory_path):
    """Create directory if it doesn't exist."""
    Path(directory_path).mkdir(parents=True, exist_ok=True)


def get_human_decision(current_balance):
    """
    Get a decision from the human player.

    Args:
        game_context (str): Context about the game state
        current_balance (int): Current amount of money the human player has

    Returns:
        int: The amount decided by the human player
    """
    max_investment = current_balance // 2  # 50% of current balance
    # print("\n===== HUMAN PLAYER'S TURN =====")

    print(f"You can invest up to {max_investment} currency units (50% of {current_balance}).")
    print("How much will you send to Player B?\n")

    while True:
        try:
            decision = int(input("Your decision: "))
            if 0 <= decision <= max_investment:
                return decision
            else:
                print(f"Please enter a number between 0 and {max_investment}.")
        except ValueError:
            print("Please enter a valid number.")


def calculate_return(player_b_profile, amount_sent, round_num, total_rounds):
    """
    Calculate a fair return amount based on Player B's profile parameters.

    Args:
        player_b_profile (dict): Player B's profile containing parameters
        amount_sent (int): Amount sent by human player
        round_num (int): Current round number
        total_rounds (int): Total number of rounds in the game

    Returns:
        int: Calculated fair return amount
    """
    params = player_b_profile["parameters"]

    # Calculate base return (50% of received amount)

    loc_value = params["base_fairness"] + params["generosity_bias"]

    print(
        f"amount_sent: {amount_sent}, large_investment_cutoff: {params['large_investment_cutoff']}, loc_value: {loc_value}"
    )

    if amount_sent > params["large_investment_cutoff"]:
        loc_value -= params["large_investment_bias"]

    print(f"loc_value: {loc_value}")

    base_return_rate = np.random.normal(
        loc_value,
        params["fairness_variance"],
    )

    print(f"base_return_rate: {base_return_rate}")

    base_return = (amount_sent * PROLIFERATION_FACTOR) * base_return_rate

    # Adjust for end game effect
    if round_num > total_rounds * 0.8:  # Last 20% of rounds
        base_return *= 1 - params["end_game_fairness_drop"]

    # Ensure return is within valid range
    max_return = amount_sent * PROLIFERATION_FACTOR
    return min(max(0, round(base_return)), max_return)


def generate_player_b_decision(prompt, player_type, session_id=1, round_num=1):
    """
    Generate a decision for Player B using the DeepSeek API.

    Args:
        prompt (str): The complete prompt for Player B
        player_type (str): The type of Player B (for logging)
        session_id (int): Identifier for the current session
        round_num (int): The current round number

    Returns:
        int: The amount decided by Player B
    """
    client = OpenAI()

    try:
        completion = client.responses.parse(
            model="gpt-4o-mini",
            input=[
                {
                    "role": "system",
                    "content": f"You are simulating a {player_type} Player B (trustee) in an economic investment game experiment. You must make decisions based on your personality profile and the game context.",
                },
                {"role": "user", "content": prompt},
            ],
            text_format=Response,
        )
        response = completion.output_parsed
        # response = completion.choices[0].message.content

        print(f"\n===== PLAYER B {player_type} RESPONSE =====")
        print(f"Amount returned: {response.amount_returned}")
        print(f"Message: {response.message}")
        print("=" * 120)

        return response

    except Exception as e:
        print(f"Request to OpenAI API failed: {e}")
        return 0


def select_random_profile():
    """
    Select a random Player B profile from personalities.toml.

    Returns:
        dict: Selected Player B profile
    """
    profile_path = Path(__file__).parent.parent / "profiles" / "personalities.toml"
    with open(profile_path, "r") as file:
        personalities = toml.load(file)

    # Randomly select a profile
    profile_id = random.choice(list(personalities.keys()))
    # profile_id = "opportunist"
    profile = personalities[profile_id]
    profile["profile_id"] = profile_id  # Add profile_id to the profile

    print(f"\nSelected Player B profile: {profile_id}")
    print(f"Description: {profile['description']}")

    return profile


def simulate_player_b_decision(player_b_profile, amount_sent, history="", session_id=1, round_num=1, total_rounds=7):
    """Simulate Player B's decision with logging."""
    player_b_type = player_b_profile["profile_id"]
    large_investment_cutoff = player_b_profile["parameters"]["large_investment_cutoff"]

    # Calculate the proliferated amount and total amount B has
    proliferated_amount = amount_sent * PROLIFERATION_FACTOR
    total_amount = 10 + proliferated_amount  # B's initial 10 + the proliferated amount

    # Calculate fair return based on profile parameters
    fair_return = calculate_return(player_b_profile, amount_sent, round_num, total_rounds)

    # Create the prompt using the template from Player B's profile
    prompt_template = player_b_profile["prompt_template"]["template"]
    prompt = prompt_template.format(
        amount_sent=amount_sent,
        proliferated_amount=proliferated_amount,
        total_amount=total_amount,
        large_investment_cutoff=large_investment_cutoff,
        history=history,
        fair_return=fair_return,
    )

    # Generate and return Player B's decision
    return generate_player_b_decision(prompt, player_b_type, session_id=session_id, round_num=round_num)


def log_transaction(session_id, round_num, player_b_profile, amount_sent, amount_returned, message="", file_path=None):
    """Log transaction details to a JSONL file."""
    # Create directory structure
    dir_path = Path("transactions") / f"session_{session_id:03d}"
    ensure_directory_exists(dir_path)

    # Create the transaction file path
    file_path = dir_path / "transactions.jsonl"

    # Create transaction record
    transaction = {
        "session_id": session_id,
        "round": round_num,
        "timestamp": datetime.datetime.now().isoformat(),
        "player_b_profile": player_b_profile,
        "amount_sent": amount_sent,
        "amount_returned": amount_returned,
        "message": message,
        "human_profit": amount_returned - amount_sent if amount_sent > 0 else 0,
        "ai_profit": (amount_sent * PROLIFERATION_FACTOR) - amount_returned if amount_sent > 0 else 0,
    }

    # Append transaction to file
    with open(file_path, "a") as file:
        file.write(json.dumps(transaction) + "\n")

    # print(f"Transaction logged to {file_path}")


def play_round(
    player_b_profile, session_id=1, round_num=1, history=None, human_balance=10, total_rounds=7, amount_sent=0
):
    """Play a complete round with human and AI interaction."""
    player_b_type = player_b_profile["profile_id"]

    print(f"\n===== ROUND {round_num} =====")
    print(f"Session: {session_id}")
    # print("=" * 50)

    # Initialize amount_returned
    amount_returned = 0
    message = ""  # 기본값 할당

    # If human sent something, get AI's response
    if amount_sent > 0:
        response = simulate_player_b_decision(
            player_b_profile,
            amount_sent,
            history=history,
            session_id=session_id,
            round_num=round_num,
            total_rounds=total_rounds,
        )

        amount_returned = response.amount_returned
        message = response.message

        # Validate Player B's return (can't return more than received)
        max_return = amount_sent * PROLIFERATION_FACTOR
        if amount_returned > max_return:
            print(
                f"Warning: Player B returned {amount_returned} which exceeds the maximum possible {max_return}. Clamping."
            )
            amount_returned = max_return

    # Log the transaction
    log_transaction(session_id, round_num, player_b_type, amount_sent, amount_returned, message)

    # Calculate new balance for human player
    new_balance = human_balance - amount_sent + amount_returned

    # Print round summary
    print(f"\nRound {round_num} summary:")
    if amount_sent * PROLIFERATION_FACTOR != 0:
        percent = amount_returned * 100 / (amount_sent * PROLIFERATION_FACTOR)
        message = f"You sent {amount_sent} and received {amount_returned} ({percent:.1f} % of total revenue)."
    else:
        message = f"You sent {amount_sent} and received {amount_returned} (N/A % of total revenue)."
    print(message)
    if amount_sent > 0:
        # print(f"Player B received: {amount_sent * 3}")
        # print(f"Player B returned: {amount_returned}")
        print(
            f"Profits: A) {amount_returned - amount_sent}. B) {(amount_sent * PROLIFERATION_FACTOR) - amount_returned}"
        )
    else:
        print("Game ended with no exchange.")
    print(f"Your balance: {new_balance}")

    return {"amount_sent": amount_sent, "amount_returned": amount_returned, "new_balance": new_balance}


def play_game(session_id=1):
    """Play a complete 7-round game."""
    # Select a random Player B profile
    player_b_profile = select_random_profile()

    history = []
    total_human_profit = 0
    total_ai_profit = 0
    human_balance = INITIAL_BALANCE  # Initial balance

    for round_num in range(1, NUM_ROUNDS + 1):
        # Build game context based on history

        # Play the round
        round_result = play_round(player_b_profile, session_id, round_num, history, human_balance, total_rounds)
        history.append(round_result)
        human_balance = round_result["new_balance"]  # Update human's balance

        # Update total profits
        if round_result["amount_sent"] > 0:
            total_human_profit += round_result["amount_returned"] - round_result["amount_sent"]
            total_ai_profit += (round_result["amount_sent"] * PROLIFERATION_FACTOR) - round_result["amount_returned"]

    # Print final game summary
    print("\n===== GAME SUMMARY =====")
    print(f"Total Rounds: {NUM_ROUNDS}")
    print(f"Your Final Balance: {human_balance}")
    print(f"Your Total Profit: {total_human_profit}")
    print(f"Player B's Total Profit: {total_ai_profit}")
    print("=" * 50)

    return history


if __name__ == "__main__":
    # Play a complete game
    play_game()
