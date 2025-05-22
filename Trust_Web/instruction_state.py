import reflex as rx
import toml
from typing import List, Dict, Any
from pathlib import Path

GAME_RULES_FILE_PATH = Path(__file__).parent / "profiles" / "game_rules.toml"


class InstructionState(rx.State):
    """Manages loading and displaying game instructions."""

    _raw_game_rules: Dict[str, Any] = {}
    current_game_for_instructions: str = ""
    error_message: str = ""

    def _ensure_rules_loaded(self):
        if not self._raw_game_rules:
            print(f"[InstructionState] _ensure_rules_loaded: Attempting to load game rules from {GAME_RULES_FILE_PATH}")
            try:
                with open(GAME_RULES_FILE_PATH, "r", encoding="utf-8") as f:
                    self._raw_game_rules = toml.load(f)
                print(
                    f"[InstructionState] _ensure_rules_loaded: Successfully loaded rules. Keys: {list(self._raw_game_rules.keys())}"
                )
            except FileNotFoundError:
                self.error_message = f"Game rules file not found: {GAME_RULES_FILE_PATH}"
                self._raw_game_rules = {}
                print(f"[InstructionState] _ensure_rules_loaded: FileNotFoundError. Path: {GAME_RULES_FILE_PATH}")
            except Exception as e:
                self.error_message = f"Error loading game rules: {str(e)}"
                self._raw_game_rules = {}
                print(f"[InstructionState] _ensure_rules_loaded: Exception loading rules: {type(e).__name__}: {e}")
        else:
            print("[InstructionState] _ensure_rules_loaded: Rules already loaded.")

    @rx.var
    def current_game_config(self) -> Dict[str, Any]:
        self._ensure_rules_loaded()
        return self._raw_game_rules.get(self.current_game_for_instructions, {})

    @rx.var
    def current_game_title(self) -> str:
        return self.current_game_config.get("title", "Instructions")

    @rx.var
    def current_game_rules(self) -> List[str]:
        return self.current_game_config.get("rules", [])

    @rx.var
    def current_game_next_page_text(self) -> str:
        print(f"[DEBUG] current_game_next_page_text: {self.current_game_config.get('next_page_text', 'Next')}")
        return self.current_game_config.get("next_page_text", "Next")

    @rx.var
    def current_game_next_page_url(self) -> str:
        print(f"[DEBUG] current_game_next_page_url: {self.current_game_config.get('next_page_url', '/')}")
        return self.current_game_config.get("next_page_url", "/")  # Default to home if not specified

    @rx.event
    def prepare_instructions(self, game_name: str):
        """Sets the current game and navigates to the instructions page."""
        self._ensure_rules_loaded()
        self.current_game_for_instructions = game_name
        self.error_message = ""  # Clear any previous errors

        # Check if the game_name is valid
        if game_name not in self._raw_game_rules:
            self.error_message = f"Instructions for game '{game_name}' not found."
            # Potentially redirect to an error page or stay and show message
            return rx.redirect("/")  # Or some error indication page

        # If game name is valid, redirect to the generic instructions page
        # The on_load of the instructions page can also take query params if needed.
        # For example, if instructions page itself needs to call prepare_instructions if game is in URL.
        return rx.redirect(f"/app/instructions?game={game_name}")

    @rx.event
    def load_instructions_for_current_page(self):
        """Sets current_game_for_instructions based on URL query param 'game' or uses already set one."""
        game_name_from_url = self.router.page.params.get("game", "")
        self._ensure_rules_loaded()  # Ensure rules are available

        if game_name_from_url:
            if game_name_from_url in self._raw_game_rules:
                self.current_game_for_instructions = game_name_from_url
                self.error_message = ""
                print(f"[InstructionState] Loaded instructions for: {game_name_from_url} from URL param.")
            else:
                self.error_message = f"Instructions for game '{game_name_from_url}' (from URL) not found."
                self.current_game_for_instructions = ""  # Clear if invalid game from URL
                print(self.error_message)
        elif self.current_game_for_instructions and self.current_game_for_instructions in self._raw_game_rules:
            # If no game in URL, but a valid game is already set in state, keep it.
            print(f"[InstructionState] Using already set game: {self.current_game_for_instructions}")
            pass
        elif self._raw_game_rules:  # No game in URL, nothing valid set, try defaulting
            first_game_in_rules = next(iter(self._raw_game_rules), None)
            if first_game_in_rules:
                self.current_game_for_instructions = first_game_in_rules
                self.error_message = ""
                print(f"[InstructionState] No game in URL or state, defaulting to first game: {first_game_in_rules}")
            else:
                self.error_message = "No game specified and no game rules found to default to."
                print(self.error_message)
        else:
            self.error_message = "No game rules loaded."
            print(self.error_message)
