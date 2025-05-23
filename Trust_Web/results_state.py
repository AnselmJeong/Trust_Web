import reflex as rx
import json
import asyncio
from Trust_Web.firebase_db import get_user_experiment_data

# get_experiment_statistics is not directly used by ResultsState anymore, so removing for now
from Trust_Web.authentication import AuthState


class ResultsState(rx.State):
    """State for the results page logic."""

    statistics: list = []  # This will hold the raw data for the currently selected game tab
    current_game_loaded: str = ""  # To track which game's data is in statistics

    @rx.event
    async def load_experiment_data(self, game_name: str, section_no: int = 1):
        """Load experiment statistics for a specific game."""
        print(f"[ResultState] load_experiment_data called for game: {game_name}!")
        self.current_game_loaded = game_name  # Store the game name
        try:
            auth_state = await self.get_state(AuthState)
            if (
                auth_state
                and hasattr(auth_state, "is_authenticated")
                and auth_state.is_authenticated
                and hasattr(auth_state, "user_id")
                and auth_state.user_id
            ):
                current_user_id = auth_state.user_id
                print(
                    f"[ResultState] User ID from AuthState: {current_user_id}, loading data for game: {game_name}"
                )
                self.statistics = get_user_experiment_data(
                    current_user_id, game_name, section_no
                )
                if not self.statistics:
                    print(
                        f"[ResultState] No experiment data found for user: {current_user_id}, game: {game_name}"
                    )
                    self.statistics = []
                else:
                    print(
                        f"[ResultState] Statistics loaded for game {game_name}: {len(self.statistics)} items"
                    )
            else:
                print(
                    "[ResultState] User not authenticated or user_id not found in AuthState."
                )
                if auth_state:
                    print(
                        f"[ResultState] AuthState details: is_authenticated={getattr(auth_state, 'is_authenticated', 'N/A')}, user_id={getattr(auth_state, 'user_id', 'N/A')}"
                    )
                else:
                    print("[ResultState] AuthState is None after await.")
                self.statistics = [
                    {"error": "User not authenticated or user_id not available"}
                ]
        except Exception as e:
            print(
                f"[ResultState] Error in load_experiment_data for game {game_name}: {e}"
            )
            self.statistics = [{"error_loading": str(e)}]

    @rx.var
    def pgg_overall_summary(self) -> dict:
        """Calculates overall summary statistics for the Public Goods Game."""
        default_summary = {
            "total_rounds": 0,
            "total_contribution": 0,
            "avg_contribution": 0,
            "total_payoff": 0,
            "avg_payoff": 0,
        }
        if self.current_game_loaded != "public_goods_game" or not self.statistics:
            return default_summary
        # Check for error state after ensuring statistics is not empty
        if isinstance(self.statistics[0], dict) and (
            "error" in self.statistics[0] or "error_loading" in self.statistics[0]
        ):
            return default_summary

        contributions = []
        payoffs = []
        num_rounds = 0

        for item in self.statistics:
            if isinstance(item, dict) and "data" in item:
                data = item.get("data", {})
                if data.get("game_name") == "public goods game":
                    try:
                        contribution = data.get("human_contribution")
                        payoff = data.get("human_payoff")
                        if (
                            data.get("round") is not None
                            and isinstance(contribution, (int, float))
                            and isinstance(payoff, (int, float))
                        ):
                            contributions.append(contribution)
                            payoffs.append(payoff)
                            num_rounds += 1
                        else:
                            print(
                                f"[PGG Overall Summary DEBUG] Skipping item due to missing/non-numeric round/contribution/payoff: {data}"
                            )
                    except (KeyError, TypeError) as e:
                        print(
                            f"[PGG Overall Summary DEBUG] Error processing item {data}: {e}"
                        )
                        continue
                else:
                    print(
                        f"[PGG Overall Summary DEBUG] Skipping item, game_name mismatch. Expected: 'public goods game', Got: '{data.get('game_name')}'. Data: {data}"
                    )

        if num_rounds == 0:
            return default_summary

        total_contribution = sum(contributions)
        total_payoff = sum(payoffs)
        avg_contribution = total_contribution / num_rounds if num_rounds > 0 else 0
        avg_payoff = total_payoff / num_rounds if num_rounds > 0 else 0

        return {
            "total_rounds": num_rounds,
            "total_contribution": round(total_contribution, 2),
            "avg_contribution": round(avg_contribution, 2),
            "total_payoff": round(total_payoff, 2),
            "avg_payoff": round(avg_payoff, 2),
        }

    @rx.var
    def has_pgg_data_to_display(self) -> bool:
        """Checks if there is PGG data to display based on total_rounds."""
        # self.pgg_overall_summary is already a reactive var that returns a dictionary.
        # Accessing an item in it should also be reactive.
        summary = self.pgg_overall_summary  # Get the dictionary
        return summary.get("total_rounds", 0) > 0

    @rx.var
    def pgg_round_summary(self) -> list[dict]:
        """Processes statistics to get PGG round summary if PGG data is loaded."""
        if self.current_game_loaded != "public_goods_game" or not self.statistics:
            return []
        if isinstance(self.statistics[0], dict) and (
            "error" in self.statistics[0] or "error_loading" in self.statistics[0]
        ):
            return []

        rounds_data = []
        for item in self.statistics:
            if isinstance(item, dict) and "data" in item:
                data = item.get("data", {})
                try:
                    if data.get("game_name") == "public goods game":
                        round_num = data.get("round")
                        contribution = data.get("human_contribution", 0)
                        payoff = data.get("human_payoff", 0)

                        if not all(
                            isinstance(val, (int, float))
                            for val in [round_num, contribution, payoff]
                        ):
                            print(
                                f"[ResultState-PGG_Round_Summary DEBUG] Skipping item with non-numeric data: {item}"
                            )
                            continue

                        rounds_data.append(
                            {
                                "round_number": int(round_num),
                                "contribution": contribution,
                                "payoff": payoff,
                            }
                        )
                except KeyError as e:
                    print(
                        f"[ResultState-PGG_Round_Summary DEBUG] KeyError processing item {item}: {e}"
                    )
                except TypeError as e:
                    print(
                        f"[ResultState-PGG_Round_Summary DEBUG] TypeError processing item {item} (likely non-numeric data): {e}"
                    )
        return sorted(rounds_data, key=lambda x: x["round_number"])

    @rx.var
    def tg_section1_summary(self) -> dict:
        """Calculates summary statistics for Trust Game Section 1."""
        default_tg_summary = {
            "total_rounds": 0,
            "total_amount_sent": 0,
            "avg_amount_sent": 0,
            "total_amount_returned": 0,
            "avg_amount_returned": 0,
            "player_a_balance": 0,
            "user_balance": 0,
            "player_a_payoff": 0,
            "user_payoff": 0,
        }
        if self.current_game_loaded != "trust_game" or not self.statistics:
            return default_tg_summary
        if isinstance(self.statistics[0], dict) and (
            "error" in self.statistics[0]
            or "error_loading" in self.statistics[0]
            or "error_fetching" in self.statistics[0]
        ):
            return default_tg_summary

        total_rounds, player_a_balance, player_b_balance = 0, 0, 0
        list_amount_sent, list_amount_returned = [], []
        list_player_a_payoff, list_player_b_payoff = [], []

        for item in self.statistics:
            if isinstance(item, dict) and "data" in item:
                data = item.get("data", {})
                if (
                    data.get("game_name") == "trust_game"
                    and data.get("section_num") == 1
                ):
                    total_rounds += 1
                    list_amount_sent.append(data.get("amount_sent", 0))
                    list_amount_returned.append(data.get("amount_returned", 0))
                    list_player_a_payoff.append(data.get("player_a_payoff", 0))
                    list_player_b_payoff.append(data.get("player_b_payoff", 0))
                    player_a_balance = data.get("player_a_balance", 0)
                    player_b_balance = data.get("player_b_balance", 0)

        total_amount_sent = sum(list_amount_sent)
        avg_amount_sent = (
            total_amount_sent / len(list_amount_sent) if list_amount_sent else 0
        )
        total_amount_returned = sum(list_amount_returned)
        avg_amount_returned = (
            total_amount_returned / len(list_amount_returned)
            if list_amount_returned
            else 0
        )
        total_player_a_payoff = sum(list_player_a_payoff)
        avg_player_a_payoff = (
            total_player_a_payoff / len(list_player_a_payoff)
            if list_player_a_payoff
            else 0
        )
        total_player_b_payoff = sum(list_player_b_payoff)
        avg_player_b_payoff = (
            total_player_b_payoff / len(list_player_b_payoff)
            if list_player_b_payoff
            else 0
        )
        #             if data.get("document_type") == "section_summary":
        #                 summary_doc = data
        #                 print(f"[TG S1 Summary DEBUG] Found S1 summary doc: {summary_doc}")
        #             elif data.get("round") is not None: # It's a round document
        #                 rounds_data.append(data)

        # if not rounds_data and not summary_doc:
        #     print("[TG S1 Summary DEBUG] No S1 rounds or summary doc found in statistics.")
        #     return default_tg_summary

        # Calculate from rounds data

        # print(f"[TG S1 Summary DEBUG] Statistics: {self.statistics}")
        # num_rounds = len(rounds_data)
        # opponent_amounts_sent = [d.get("amount_sent", 0) for d in rounds_data] # Player A sent
        # my_amounts_returned = [d.get("amount_returned", 0) for d in rounds_data] # Player B returned

        # total_opponent_sent = sum(opponent_amounts_sent)
        # avg_opponent_sent = total_opponent_sent / num_rounds if num_rounds > 0 else 0
        # total_my_returned = sum(my_amounts_returned)
        # avg_my_returned = total_my_returned / num_rounds if num_rounds > 0 else 0

        # # Get final balances from summary doc if available, otherwise they remain 0
        # user_final_balance_s1 = summary_doc.get("user_final_balance", 0) if summary_doc else 0
        # opponent_final_balance_s1 = summary_doc.get("opponent_final_balance", 0) if summary_doc else 0

        # If summary doc exists, it might also have a round count, but we prioritize actual rounds for consistency
        # However, if only summary exists (e.g. rounds failed to load but summary did), we can use its info
        # For now, num_rounds from actual round data is primary.

        summary = {
            "total_rounds": total_rounds,
            "total_amount_sent": round(total_amount_sent, 2),
            "avg_amount_sent": round(avg_amount_sent, 2),
            "total_amount_returned": round(total_amount_returned, 2),
            "avg_amount_returned": round(avg_amount_returned, 2),
            "player_a_payoff": round(avg_player_a_payoff, 2),
            "user_payoff": round(avg_player_b_payoff, 2),
            "player_a_balance": round(player_a_balance, 2),
            "user_balance": round(player_b_balance, 2),
        }
        print(f"[TG S1 Summary DEBUG] Calculated S1 summary: {summary}")
        return summary

    @rx.var
    def has_tg_section1_data_to_display(self) -> bool:
        """Checks if there is Trust Game Section 1 data to display."""
        # Check based on total rounds in the computed summary
        summary = self.tg_section1_summary
        return summary.get("total_rounds", 0) > 0

    @rx.var
    def formatted_statistics(self) -> str:
        """Return the raw statistics list formatted as a JSON string."""
        if not self.statistics:
            return json.dumps([], indent=2)
        if isinstance(self.statistics[0], dict) and (
            "error" in self.statistics[0] or "error_loading" in self.statistics[0]
        ):
            return json.dumps(self.statistics[0], indent=2)
        return json.dumps(self.statistics, indent=2)

    @rx.var
    def tg_section1_round_chart_data(self) -> list[dict]:
        """Returns per-round data for S1 line charts."""
        rounds = []
        for item in self.statistics:
            if isinstance(item, dict) and "data" in item:
                data = item["data"]
                if (
                    data.get("game_name") == "trust_game"
                    and data.get("section_num") == 1
                    and data.get("round") is not None
                ):
                    rounds.append(
                        {
                            "round": data.get("round"),
                            "amount_sent": data.get("amount_sent", 0),
                            "amount_returned": data.get("amount_returned", 0),
                            "player_a_payoff": data.get("player_a_payoff", 0),
                            "user_payoff": data.get("player_b_payoff", 0),
                            "player_a_balance": data.get("player_a_balance", 0),
                            "user_balance": data.get("player_b_balance", 0),
                        }
                    )
        # Sort by round number
        return sorted(rounds, key=lambda x: x["round"])

    @rx.var
    def tg_section2_summary(self) -> dict:
        """Calculates summary statistics for Trust Game Section 2."""

        print(f"[TG S2 Summary DEBUG] {self.current_game_loaded}")
        default_tg_summary = {
            "total_rounds": 0,
            "total_amount_sent": 0,
            "avg_amount_sent": 0,
            "total_amount_returned": 0,
            "avg_amount_returned": 0,
            "player_b_balance": 0,
            "user_balance": 0,
            "player_b_payoff": 0,
            "user_payoff": 0,
        }
        # if self.current_game_loaded != "trust_game" or not self.statistics:
        #     print(
        #         f"[TG S2 Summary DEBUG] No statistics found for game: {self.current_game_loaded}"
        #     )
        #     return default_tg_summary
        # if isinstance(self.statistics[0], dict) and (
        #     "error" in self.statistics[0]
        #     or "error_loading" in self.statistics[0]
        #     or "error_fetching" in self.statistics[0]
        # ):
        #     return default_tg_summary

        total_rounds, human_balance, player_b_balance = 0, 0, 0
        list_amount_sent, list_amount_returned = [], []
        list_human_payoff, list_player_b_payoff = [], []

        for item in self.statistics:
            if isinstance(item, dict) and "data" in item:
                data = item.get("data", {})
                if (
                    data.get("game_name") == "trust_game"
                    and data.get("section_num") == 2
                ):
                    total_rounds += 1
                    list_amount_sent.append(data.get("amount_sent", 0))
                    list_amount_returned.append(data.get("amount_returned", 0))
                    list_human_payoff.append(data.get("human_payoff", 0))
                    list_player_b_payoff.append(data.get("player_b_payoff", 0))
                    human_balance = data.get("human_balance", 0)
                    player_b_balance = data.get("player_b_balance", 0)

        total_amount_sent = sum(list_amount_sent)
        avg_amount_sent = (
            total_amount_sent / len(list_amount_sent) if list_amount_sent else 0
        )
        total_amount_returned = sum(list_amount_returned)
        avg_amount_returned = (
            total_amount_returned / len(list_amount_returned)
            if list_amount_returned
            else 0
        )
        total_human_payoff = sum(list_human_payoff)
        avg_human_payoff = (
            total_human_payoff / len(list_human_payoff) if list_human_payoff else 0
        )
        total_player_b_payoff = sum(list_player_b_payoff)
        avg_player_b_payoff = (
            total_player_b_payoff / len(list_player_b_payoff)
            if list_player_b_payoff
            else 0
        )

        summary = {
            "total_rounds": total_rounds,
            "total_amount_sent": round(total_amount_sent, 2),
            "avg_amount_sent": round(avg_amount_sent, 2),
            "total_amount_returned": round(total_amount_returned, 2),
            "avg_amount_returned": round(avg_amount_returned, 2),
            "player_b_balance": round(player_b_balance, 2),
            "user_balance": round(human_balance, 2),
            "player_b_payoff": round(avg_player_b_payoff, 2),
            "user_payoff": round(avg_human_payoff, 2),
        }

        return summary

    @rx.var
    def has_tg_section2_data_to_display(self) -> bool:
        """Checks if there is Trust Game Section 2 data to display."""

        print("[TG S2 Summary DEBUG] has_tg_section2_data_to_display")
        summary = self.tg_section2_summary
        print(f"[TG S2 Summary DEBUG] Summary: {summary}")
        return summary.get("total_rounds", 0) > 0

    @rx.var
    def tg_section2_round_chart_data(self) -> list[dict]:
        """Returns per-round data for S2 line charts."""
        rounds = []
        for item in self.statistics:
            if isinstance(item, dict) and "data" in item:
                data = item["data"]
                if (
                    data.get("game_name") == "trust_game"
                    and data.get("section_num") == 2
                    and data.get("round") is not None
                ):
                    rounds.append(
                        {
                            "round": data.get("round"),
                            "stage": data.get("stage_num"),
                            "stage_round": f"{data.get('stage_num', 0) + 1}-{data.get('round', 0)}",
                            "amount_sent": data.get("amount_sent", 0),
                            "amount_returned": data.get("amount_returned", 0),
                            "user_payoff": data.get("human_payoff", 0),
                            "player_b_payoff": data.get("player_b_payoff", 0),
                            "user_balance": data.get("human_balance", 0),
                            "player_b_balance": data.get("player_b_balance", 0),
                        }
                    )
        # Sort by stage and then round number
        return sorted(rounds, key=lambda x: (x["stage_round"]))

    @rx.var
    def tg_section2_stage_round_ticks(self) -> list:
        """Return a list of stage_round values for x-axis ticks (e.g., 1-1, 1-6, 2-1, 2-6, ...)."""
        all_points = self.tg_section2_round_chart_data
        ticks = [pt["stage_round"] for pt in all_points if pt["round"] in (1, 6)]
        # 중복 제거 및 stage, round 기준 정렬
        return sorted(
            set(ticks), key=lambda x: (int(x.split("-")[0]), int(x.split("-")[1]))
        )
