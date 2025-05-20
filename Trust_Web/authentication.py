import reflex as rx
from .firebase_config import sign_in_with_email_and_password, create_user_with_email_and_password
from .questionnaire_state import QuestionnaireState
from .demographic_state import DemographicState
from .trust_game_state import TrustGameState

# from .questionnaire_state import QuestionnaireState # Removed
# from .trust_game_state import TrustGameState  # Needed for TrustGameState.reset_game_state event # Removed


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

    @rx.event
    def login(self) -> None:
        """Handle user login using Firebase."""
        try:
            if not self.user_email or not self.password:
                self.auth_error = "Please enter both email and password"
                return

            user = sign_in_with_email_and_password(self.user_email, self.password)
            raw_user_id = user.get("localId")

            if not raw_user_id:
                self.auth_error = "Failed to retrieve user ID from login."
                print(f"[AUTH_STATE] Login error: localId is missing or empty. User: {user}")
                return

            self.user_id = raw_user_id
            self.is_authenticated = True
            self.auth_error = ""
            print(f"[AUTH_STATE] Login successful. User ID set to: {self.user_id}, Auth: {self.is_authenticated}")
            print(
                f"[AUTH_STATE] Calling QuestionnaireState.set_user_identity with: id={self.user_id}, email={self.user_email}"
            )

            return [
                AuthState.close_login_modal,
                QuestionnaireState.set_user_identity(self.user_id, self.user_email),
                DemographicState.set_user_identity(self.user_id, self.user_email),
                rx.redirect("/app/demography"),
            ]
        except Exception as e:
            self.auth_error = str(e)
            print(f"[AUTH_STATE] Login exception: {e}")

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
            raw_user_id = user.get("localId")

            if not raw_user_id:
                self.auth_error = "Failed to retrieve user ID from registration."
                print(f"[AUTH_STATE] Register error: localId is missing or empty. User: {user}")
                return

            self.user_id = raw_user_id
            self.is_authenticated = True
            self.auth_error = ""
            print(f"[AUTH_STATE] Register successful. User ID set to: {self.user_id}, Auth: {self.is_authenticated}")
            print(
                f"[AUTH_STATE] Calling QuestionnaireState.set_user_identity with: id={self.user_id}, email={self.user_email}"
            )

            return [
                AuthState.close_login_modal,
                QuestionnaireState.set_user_identity(self.user_id, self.user_email),
                DemographicState.set_user_identity(self.user_id, self.user_email),
                rx.redirect("/app/demography"),
            ]
        except Exception as e:
            self.auth_error = str(e)
            print(f"[AUTH_STATE] Register exception: {e}")

    @rx.event
    def logout(self) -> None:
        """Handle user logout."""
        prev_user_id = self.user_id
        prev_auth_state = self.is_authenticated

        self.user_email = ""
        self.password = ""
        self.confirm_password = ""  # Ensure confirm_password is also cleared
        self.is_authenticated = False
        self.user_id = ""
        self.auth_error = ""  # Clear any auth errors on logout

        print(
            f"[AUTH_STATE] Logout. Prev UserID: {prev_user_id}, Prev Auth: {prev_auth_state}, New Auth: {self.is_authenticated}"
        )

        return [
            TrustGameState.reset_game_state,  # Call reset_game_state from TrustGameState
            rx.redirect("/"),
        ]

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
