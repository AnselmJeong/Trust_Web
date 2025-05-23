import reflex as rx
from .firebase_config import sign_in_with_email_and_password, create_user_with_email_and_password
# Removed direct state imports, will rely on events
# from .questionnaire_state import QuestionnaireState
# from .demographic_state import DemographicState
# from .trust_game_state import TrustGameState
# from .public_goods_state import PublicGoodState
# from .components.results import ResultsState # Removed this line


class AuthState(rx.State):
    """Handles user authentication and session management."""

    # Authentication state
    user_email: str = ""
    password: str = ""
    confirm_password: str = ""
    is_authenticated: bool = False
    auth_error: str = ""
    user_id: str = ""  # Firebase localId

    # Modal state for login dialog
    show_login_modal: bool = False

    @rx.event
    def set_user_email(self, value: str) -> None:
        """Set the user email."""
        self.user_email = value

    @rx.event
    def set_password(self, value: str) -> None:
        """Set the user password."""
        self.password = value

    @rx.event
    def set_confirm_password(self, value: str) -> None:
        """Set the confirm password."""
        self.confirm_password = value

    def _handle_successful_auth(self, user: dict, redirect_path: str = "/app/demography"):
        """Private helper to handle common logic after successful login/registration."""
        raw_user_id = user.get("localId")
        if not raw_user_id:
            self.auth_error = "Failed to retrieve user ID from authentication."
            print(f"[AUTH_STATE] Auth error: localId is missing or empty. User: {user}")
            return self.auth_error # Or raise an exception

        self.user_id = raw_user_id
        self.is_authenticated = True
        self.auth_error = ""
        print(f"[AUTH_STATE] Authentication successful. User ID: {self.user_id}, Email: {self.user_email}, Auth: {self.is_authenticated}")

        # Emit an event to notify other states, instead of direct calls
        event_payload = {"user_id": self.user_id, "user_email": self.user_email}
        
        actions = [
            AuthState.close_login_modal,
            rx.Event("auth.set_user_identity", payload=event_payload),
            rx.redirect(redirect_path)
        ]
        return actions

    @rx.event
    def login(self) -> None:
        """Handle user login using Firebase."""
        try:
            if not self.user_email or not self.password:
                self.auth_error = "Please enter both email and password"
                return
            user = sign_in_with_email_and_password(self.user_email, self.password)
            return self._handle_successful_auth(user)
        except Exception as e:
            self.auth_error = str(e)
            print(f"[AUTH_STATE] Login exception: {e}")
            # Optionally, return an error state or None
            return AuthState.set_auth_error(str(e))


    @rx.event
    def register(self) -> None:
        """Handle user registration using Firebase."""
        try:
            if not self.user_email or not self.password:
                self.auth_error = "Please enter both email and password"
                return
            if self.password != self.confirm_password:
                self.auth_error = "Passwords do not match"
                return
            user = create_user_with_email_and_password(self.user_email, self.password)
            # For registration, redirect might be different or include additional setup steps
            # For now, using the default redirect_path from _handle_successful_auth
            return self._handle_successful_auth(user)
        except Exception as e:
            self.auth_error = str(e)
            print(f"[AUTH_STATE] Register exception: {e}")
            return AuthState.set_auth_error(str(e))

    @rx.event
    def logout(self) -> None:
        """Handle user logout by clearing local state and emitting a logout event."""
        prev_user_id = self.user_id
        prev_auth_state = self.is_authenticated

        self.user_email = ""
        self.password = ""
        self.confirm_password = ""
        self.is_authenticated = False
        self.user_id = ""
        self.auth_error = ""

        print(
            f"[AUTH_STATE] Logout. Prev UserID: {prev_user_id}, Prev Auth: {prev_auth_state}, New Auth: {self.is_authenticated}"
        )
        # Emit a general logout event for other states to handle
        return [
            rx.Event("auth.logout_event"),
            rx.redirect("/")
        ]

    @rx.event
    def set_auth_error(self, error_message: str):
        """Helper to set auth_error, can be returned by event handlers."""
        self.auth_error = error_message

    @rx.event
    def on_load_index_page_check(self):
        """Checks auth on index page load and redirects if necessary."""
        print(f"[AUTH_STATE-INDEX_CHECK] Auth: {self.is_authenticated}")
        if self.is_authenticated:
            # return rx.redirect("/app/demography") # Allow authenticated users to see the landing page
            return None
        return None

    @rx.event
    def on_load_app_page_check(self):
        """Checks auth on app page load and redirects if necessary."""
        print(f"[AUTH_STATE-APP_CHECK] Auth: {self.is_authenticated}, UserID: {self.user_id}")
        if not self.is_authenticated or not self.user_id:
            return rx.redirect("/")
        return None

    @rx.event
    def open_login_modal(self):
        self.show_login_modal = True

    @rx.event
    def close_login_modal(self):
        self.show_login_modal = False

    @rx.event
    def set_login_modal_state(self, open_state: bool):
        """Sets the visibility of the login modal based on the dialog's open state."""
        self.show_login_modal = open_state

    @rx.event
    def login_on_enter(self, key: str):
        if key == "Enter":
            return self.login()

    @rx.event
    def register_on_enter(self, key: str):
        if key == "Enter":
            return self.register()
