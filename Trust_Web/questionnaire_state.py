import reflex as rx
import toml
from pathlib import Path
from typing import Dict, List, Optional, Any
import datetime

# Assuming firebase_db.py is in the same directory (Trust_Web)
from .firebase_db import save_experiment_data, get_user_questionnaire_responses
# from .authentication import AuthState  # Import AuthState # Removed

# Path to the questionnaires configuration file
QUESTIONNAIRES_FILE_PATH: Path = Path(__file__).parent / "profiles" / "questionnaires.toml"
QUESTIONNAIRE_ORDER: List[str] = ["UCLA", "DASS", "TRUST"]

# Path to the game rules configuration file
GAME_RULES_FILE_PATH: Path = Path(__file__).parent / "profiles" / "game_rules.toml"


class QuestionnaireState(rx.State):
    """Manages questionnaire loading, response collection, scoring, and Firebase submission."""

    user_id: str = ""  # This is the Firebase localId
    user_email: str = ""  # Added to store user's email
    response_doc_ids: Dict[str, Optional[str]] = {}

    # Current questionnaire being managed
    current_questionnaire: str = QUESTIONNAIRE_ORDER[0]  # Default to the first questionnaire

    # Internal state for configurations and responses
    _raw_configs: Dict[str, Any] = {}
    responses: Dict[str, List[Optional[str]]] = {}
    calculated_scores: Dict[str, Optional[int]] = {}

    error_message: str = ""

    def _ensure_configs_loaded(self):
        """Loads questionnaire configurations from the TOML file if not already loaded."""
        if not self._raw_configs:
            try:
                with open(QUESTIONNAIRES_FILE_PATH, "r", encoding="utf-8") as f:
                    self._raw_configs = toml.load(f)

                for name in QUESTIONNAIRE_ORDER:  # Ensure all ordered questionnaires are initialized
                    if name in self._raw_configs:
                        config_data = self._raw_configs[name]
                        if "items" in config_data and isinstance(config_data["items"], list):
                            self.responses[name] = [None] * len(config_data["items"])
                        else:
                            print(
                                f"Warning: Questionnaire '{name}' in TOML is missing 'items' or 'items' is not a list."
                            )
                            # Potentially remove from QUESTIONNAIRE_ORDER or handle error if critical
                    else:
                        print(f"Warning: Questionnaire '{name}' from ORDER not found in TOML.")
                        # Potentially remove from QUESTIONNAIRE_ORDER or handle error

            except FileNotFoundError:
                self.error_message = f"Configuration file not found: {QUESTIONNAIRES_FILE_PATH}"
                self._raw_configs = {}
            except Exception as e:
                print(f"Detailed error loading questionnaire TOML: {type(e).__name__}: {e}")
                self.error_message = f"Error loading questionnaire configurations: {str(e)}"
                self._raw_configs = {}

    @rx.event
    def set_user_identity(self, user_id: str, user_email: str):
        """Sets the user ID and email for the questionnaire state."""
        print(f"[QUESTIONNAIRE_STATE] set_user_identity called with: id='{user_id}', email='{user_email}'")
        self.user_id = user_id
        self.user_email = user_email  # Store the email
        self.error_message = ""

        self._ensure_configs_loaded()  # Ensures self._raw_configs is populated

        # Initialize responses, scores, and doc_ids for all questionnaires in QUESTIONNAIRE_ORDER
        for q_name in QUESTIONNAIRE_ORDER:
            if q_name in self._raw_configs and "items" in self._raw_configs[q_name]:
                num_items = len(self._raw_configs[q_name]["items"])
                self.responses[q_name] = [None] * num_items
            else:
                self.responses[q_name] = []
            self.calculated_scores.pop(q_name, None)
            self.response_doc_ids[q_name] = None

        if self.user_id:  # Load existing data only if user_id is valid
            print(f"[QUESTIONNAIRE_STATE] Attempting to load responses for user: {self.user_id}")
            fetched_data = get_user_questionnaire_responses(self.user_id)
            print(f"[QUESTIONNAIRE_STATE] Fetched data from Firebase: {fetched_data}")
            for q_name, data in fetched_data.items():
                if q_name in QUESTIONNAIRE_ORDER:
                    loaded_q_responses = data.get("data", {}).get("responses")
                    if (
                        isinstance(loaded_q_responses, list)
                        and q_name in self.responses
                        and self.responses[q_name] is not None
                        and len(loaded_q_responses) == len(self.responses[q_name])
                    ):
                        self.responses[q_name] = loaded_q_responses
                        self.response_doc_ids[q_name] = data.get("doc_id")
                        print(f"[QUESTIONNAIRE_STATE] Loaded responses for {q_name}, doc_id: {data.get('doc_id')}")
                    else:
                        print(f"[QUESTIONNAIRE_STATE] Mismatch/error loading responses for {q_name}.")

        if QUESTIONNAIRE_ORDER:
            self.current_questionnaire = QUESTIONNAIRE_ORDER[0]
        else:
            self.current_questionnaire = ""
            self.error_message = "Error: No questionnaires defined in order."
        print(
            f"[QUESTIONNAIRE_STATE] User ID set to: '{self.user_id}'. Current questionnaire: '{self.current_questionnaire}'"
        )

    @rx.var
    def available_questionnaires(self) -> List[str]:
        """Returns a list of names of the available questionnaires (from order)."""
        return QUESTIONNAIRE_ORDER

    @rx.var
    def current_config(self) -> Dict[str, Any]:
        """Returns the full configuration for the current questionnaire."""
        self._ensure_configs_loaded()
        return self._raw_configs.get(self.current_questionnaire, {})

    @rx.var
    def current_items(self) -> List[str]:
        """Returns the list of items (questions) for the current questionnaire."""
        return self.current_config.get("items", [])

    @rx.var
    def current_likert_anchors(self) -> List[str]:
        """Returns the Likert scale anchors for the current questionnaire."""
        return self.current_config.get("likert_anchor", [])

    @rx.var
    def current_likert_level(self) -> Optional[int]:
        """Returns the Likert level (e.g., 4 for 0-3 scoring) for the current questionnaire."""
        return self.current_config.get("likert_level")

    @rx.var
    def current_responses(self) -> List[Optional[str]]:
        """Returns the responses for the current questionnaire."""
        self._ensure_configs_loaded()
        if self.current_questionnaire not in self.responses:
            self.responses[self.current_questionnaire] = [None] * len(self.current_items)
        return self.responses.get(self.current_questionnaire, [])

    @rx.var
    def current_likert_options_as_strings(self) -> List[str]:
        """Returns the Likert options as a list of strings (e.g., [\"0\", \"1\", \"2\"])."""
        if self.current_likert_level is not None:
            return [str(i) for i in range(self.current_likert_level)]
        return []

    @rx.event
    def set_response(self, item_index: int, value: str):
        """
        Sets the response for a specific item in the current questionnaire.
        value is expected to be a string from UI (e.g., "0", "1", "2", "3").
        """
        questionnaire_name = self.current_questionnaire  # Use the var's current value
        print(f"Setting response for {questionnaire_name}, item {item_index}, value '{value}'")

        self._ensure_configs_loaded()
        self.error_message = ""

        if questionnaire_name not in self._raw_configs:
            self.error_message = f"Questionnaire '{questionnaire_name}' not found."
            return

        items = self._raw_configs[questionnaire_name].get("items", [])

        if not (0 <= item_index < len(items)):
            self.error_message = f"Invalid item index: {item_index}."
            return

        if questionnaire_name not in self.responses or len(self.responses[questionnaire_name]) != len(items):
            self.responses[questionnaire_name] = [None] * len(items)

        self.responses[questionnaire_name][item_index] = value

        if questionnaire_name in self.calculated_scores:
            self.calculated_scores[questionnaire_name] = None

    def _calculate_score_internal(self, questionnaire_name: str) -> Optional[int]:
        q_config = self._raw_configs.get(questionnaire_name)
        q_responses = self.responses.get(questionnaire_name)

        if not q_config or not q_responses:
            self.error_message = f"Data missing for score calculation of '{questionnaire_name}'."
            return None
        if any(r is None for r in q_responses):
            self.error_message = f"Not all items answered for '{questionnaire_name}'."
            return None

        total_score = 0
        likert_level = q_config.get("likert_level")
        reverse_coded_1_indexed = q_config.get("reverse_coding", [])
        if not isinstance(reverse_coded_1_indexed, list):
            reverse_coded_1_indexed = []
        if likert_level is None:
            self.error_message = f"Likert level not defined for '{questionnaire_name}'."
            return None

        for idx, score_value_str in enumerate(q_responses):
            if score_value_str is None:
                self.error_message = f"Internal error: Missing response for item {idx + 1}."
                return None
            try:
                current_score_int = int(score_value_str)
            except ValueError:
                self.error_message = f"Internal error: Non-integer string response ('{score_value_str}')."
                return None

            item_number_1_indexed = idx + 1
            if item_number_1_indexed in reverse_coded_1_indexed:
                processed_score = (likert_level - 1) - current_score_int
            else:
                processed_score = current_score_int
            total_score += processed_score
        return total_score

    @rx.event
    def submit_questionnaire(self):
        """
        Calculates score for current questionnaire, saves/updates it, and navigates to next step.
        """
        print(
            f"[QUESTIONNAIRE_STATE] submit_questionnaire entered. Current self.user_id: '{self.user_id}', self.user_email: '{self.user_email}'"
        )
        self._ensure_configs_loaded()
        self.error_message = ""

        current_q_name = self.current_questionnaire

        if not self.user_id or not self.user_email:  # Check local copies
            self.error_message = "User ID or Email not set. Cannot save data."
            print(
                f"[QUESTIONNAIRE_STATE] Error in submit: User ID ('{self.user_id}') or Email ('{self.user_email}') is not set."
            )
            return

        if current_q_name not in self._raw_configs:
            self.error_message = f"Questionnaire '{current_q_name}' not found."
            return

        q_responses = self.responses.get(current_q_name)
        if not q_responses or any(r is None for r in q_responses):
            self.error_message = f"Please answer all items for '{current_q_name}' before submitting."
            return

        try:
            total_score = self._calculate_score_internal(current_q_name)
            if total_score is None:
                if not self.error_message:
                    self.error_message = f"Failed to calculate score for '{current_q_name}'."
                return

            self.calculated_scores[current_q_name] = total_score
            q_config = self._raw_configs[current_q_name]
            data_to_save = {
                "user_email": self.user_email,  # Use stored plain string email
                "questionnaire_name": current_q_name,
                "total_score": total_score,
                "responses": q_responses,  # These are List[Optional[str]], ensure they are List[str] if needed by schema or handle None
                "likert_level": q_config.get("likert_level"),
                "timestamp": datetime.datetime.now().isoformat(),  # Will be overwritten by server timestamp in save_experiment_data
                "game_name": "questionnaire_result",
            }

            print(f"[QUESTIONNAIRE_STATE] Data being sent to Firebase: {data_to_save}")

            save_experiment_data(self.user_id, data_to_save)
            self.error_message = ""  # Clear error on success

            # Navigate to next questionnaire or page
            current_q_index = QUESTIONNAIRE_ORDER.index(current_q_name)
            if current_q_index < len(QUESTIONNAIRE_ORDER) - 1:
                next_q_name = QUESTIONNAIRE_ORDER[current_q_index + 1]
                self.current_questionnaire = next_q_name
                self.calculated_scores.pop(next_q_name, None)  # Clear any previous score for next_q
                return None  # Stay on the same page, UI will update due to current_questionnaire change
            else:
                # Last questionnaire submitted, navigate to instructions for the first game (e.g., public_goods)
                return InstructionState.prepare_instructions("public_goods")

        except ValueError:  # Handles QUESTIONNAIRE_ORDER.index() if current_q_name is not in order
            self.error_message = f"Error finding '{current_q_name}' in questionnaire sequence."
        except Exception as e:
            self.error_message = f"Error submitting '{current_q_name}': {str(e)}"
            print(f"Detailed error during submission of {current_q_name}: {e}")
            self.calculated_scores[current_q_name] = None


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

    # Event handler for auth.set_user_identity
    @rx.event_handler("auth.set_user_identity")
    def handle_set_user_identity(self, payload: dict):
        """Handles the set_user_identity event emitted by AuthState."""
        user_id = payload.get("user_id")
        user_email = payload.get("user_email")
        if user_id is not None and user_email is not None:
            print(f"[QuestionnaireState] Received set_user_identity event. User ID: {user_id}, Email: {user_email}")
            # Call the existing set_user_identity method which also handles loading data
            self.set_user_identity(user_id, user_email)
        else:
            print("[QuestionnaireState] Error: Received set_user_identity event with missing user_id or user_email.")
