import reflex as rx
import json
import asyncio # Added import for asyncio
from Trust_Web.firebase_db import get_user_experiment_data, get_experiment_statistics
from Trust_Web.authentication import AuthState


class ResultsState(rx.State):
    """State for the results page."""

    statistics: list = []
    
    @rx.event
    async def load_statistics(self, game_name: str):
        """Load experiment statistics from Firestore using user_id from AuthState for a specific game."""
        print(f"[ResultState] load_statistics called for game: {game_name}!")
        try:
            auth_state = await self.get_state(AuthState)
            print(f"[ResultState] Type of auth_state after await: {type(auth_state)}")

            if auth_state and hasattr(auth_state, 'is_authenticated') and auth_state.is_authenticated and hasattr(auth_state, 'user_id') and auth_state.user_id:
                current_user_id = auth_state.user_id
                # Use the game_name parameter in the print statement
                print(f"[ResultState] User ID from AuthState: {current_user_id}, loading data for game: {game_name}") 
                self.statistics = get_user_experiment_data(current_user_id, game_name) 
                if not self.statistics:
                    print(f"[ResultState] No experiment data found for user: {current_user_id}, game: {game_name}")
                    self.statistics = [] 
                else:
                    print(f"[ResultState] Statistics loaded for game {game_name}: {self.statistics}")
            else:
                print("[ResultState] User not authenticated or user_id not found in AuthState.")
                if auth_state:
                    print(f"[ResultState] AuthState details: is_authenticated={getattr(auth_state, 'is_authenticated', 'N/A')}, user_id={getattr(auth_state, 'user_id', 'N/A')}")
                else:
                    print("[ResultState] AuthState is None after await.")
                self.statistics = [{'error': 'User not authenticated or user_id not available'}]
        except Exception as e:
            print(f"[ResultState] Error in load_statistics for game {game_name}: {e}")
            self.statistics = [{'error_loading': str(e)}]

    @rx.var
    def formatted_statistics(self) -> str:
        """Return the statistics list formatted as a JSON string."""
        if not self.statistics:
            return json.dumps([], indent=2)
        if isinstance(self.statistics, list) and len(self.statistics) == 1 and (
            'error' in self.statistics[0] or 'error_loading' in self.statistics[0]
        ):
            return json.dumps(self.statistics[0], indent=2)
        return json.dumps(self.statistics, indent=2)


# @rx.page(route="/app/results", title="Experiment Results", on_load=ResultsState.load_statistics)
def results_page() -> rx.Component:
    """UI for the experiment results page."""
    return rx.vstack(
        rx.heading("Experiment Results", size="7", margin_bottom="1em"),
        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger(
                    "Public Goods Game", 
                    value="pgg", 
                    on_click=ResultsState.load_statistics(game_name="public_goods_game")
                ),
                rx.tabs.trigger(
                    "Trust Game (section 1)", 
                    value="tg1", 
                    on_click=ResultsState.load_statistics(game_name="trust_game")
                ),
                rx.tabs.trigger(
                    "Trust Game (section 2)", 
                    value="tg2", 
                    on_click=ResultsState.load_statistics(game_name="trust_game")
                ),
            ),
            rx.tabs.content(
                rx.cond(
                    ResultsState.statistics,
                    rx.code_block(ResultsState.formatted_statistics, language="json", width="100%"),
                    rx.text("No statistics loaded, statistics are empty, or user not authenticated. Click a tab to load data.")
                ),
                value="pgg",
            ),
            rx.tabs.content(
                # This content will also show self.statistics, which is loaded by clicking TG1 or TG2 tabs.
                # If TG1 and TG2 need to show *different filtered views* of the "trust_game" data,
                # this rx.code_block or its displayed var will need to be more specific.
                rx.cond(
                    ResultsState.statistics,
                    rx.code_block(ResultsState.formatted_statistics, language="json", width="100%"),
                    rx.text("No statistics loaded for Trust Game. Click the tab to load data.")
                ),
                value="tg1",
            ),
            rx.tabs.content(
                # Similar to tg1, this shows the full self.statistics.
                rx.cond(
                    ResultsState.statistics,
                    rx.code_block(ResultsState.formatted_statistics, language="json", width="100%"),
                    rx.text("No statistics loaded for Trust Game. Click the tab to load data.")
                ),
                value="tg2",
            ),
            defaultValue="pgg", # This tab will be active by default, but data won't load until clicked.
            width="100%",
        ),
        align="center",
        spacing="7",
        padding_top="5em",
    ) 