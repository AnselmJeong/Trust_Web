import reflex as rx
from typing import List, Dict, Any, Optional
import datetime

# Assuming firebase_db.py is in the same directory (Trust_Web)
from .firebase_db import save_experiment_data, get_user_demographics_data


class DemographicState(rx.State):
    user_id: str = ""  # Firebase localId, to be set by AuthState
    user_email: str = ""  # User's email, to be set by AuthState
    demographics_doc_id: Optional[str] = None  # Firestore document ID for this user's demographics

    # Options for past_diagnoses - this remains as it's used for rendering in the form
    diagnosis_options: List[str] = [
        "우울증",
        "공황장애",
        "사회공포증",
        "강박장애",
        "양극성 장애",
        "불안장애",
        "적응장애",
        "대인기피증",
        "주의력 결핍장애",
        "기타 정신병적 장애",
    ]

    # Single dictionary to store all form data, including loaded data
    demographics_data: Dict[str, Any] = {}
    error_message: str = ""

    @rx.event
    def update_demographics_field(self, field_name: str, value: Any):
        """Updates a single field in the demographics_data dictionary."""
        self.demographics_data[field_name] = value
        # To ensure reactivity, especially if nested, reassign if necessary
        # For simple key-value updates at the top level, this should be fine.
        # If issues persist, consider self.demographics_data = self.demographics_data.copy()
        print(f"[DEMOGRAPHIC_STATE] Updated field '{field_name}' to: {value}")

    @rx.event
    def set_user_identity(self, user_id: str, user_email: str):
        """Sets the user ID and email, then loads existing demographic data."""
        print(f"[DEMOGRAPHIC_STATE] set_user_identity called with: id='{user_id}', email='{user_email}'")
        self.user_id = user_id
        self.user_email = user_email
        self.error_message = ""
        self.demographics_data = {}  # Reset data before loading
        self.demographics_doc_id = None  # Reset doc_id

        if self.user_id:
            self._load_demographics_from_firebase()
        else:
            print("[DEMOGRAPHIC_STATE] User ID is not set, cannot load demographics.")

    def _load_demographics_from_firebase(self):
        """Loads demographic data for the current user_id from Firebase."""
        print(f"[DEMOGRAPHIC_STATE] Attempting to load demographics for user: {self.user_id}")
        data_with_doc_id = get_user_demographics_data(self.user_id)
        if data_with_doc_id:
            self.demographics_data = data_with_doc_id.get("data", {})
            print(f"[DEMOGRAPHIC_STATE] Loaded demographics for user {self.user_id}, doc_id: {data_with_doc_id.get('doc_id')}")
        else:
            print(f"[DEMOGRAPHIC_STATE] No existing demographic data found for user: {self.user_id}")
            self.demographics_data = {}  # Ensure it's empty if nothing found

    @rx.event
    def handle_submit(self, form_data: dict):
        """Handle the form submit, add user info, and save to Firebase."""
        print(f"[DEMOGRAPHIC_STATE] handle_submit called. Raw form_data: {form_data}")
        if not self.user_id or not self.user_email:
            self.error_message = "User not properly identified. Cannot save demographics."
            print(f"[DEMOGRAPHIC_STATE] Error in submit: User ID ('{self.user_id}') or Email ('{self.user_email}') is not set.")
            return

        # Prepare data to save
        self.demographics_data = form_data.copy()  # Start with the submitted form data
        self.demographics_data["user_id"] = self.user_id  # For querying
        self.demographics_data["user_email"] = self.user_email  # Storing the email
        self.demographics_data["game_name"] = "demographics_data"  # For Firestore doc naming
        # 'timestamp' will be added by save_experiment_data using server timestamp

        print(f"[DEMOGRAPHIC_STATE] Data being sent to Firebase: {self.demographics_data}")

        try:
            save_experiment_data(self.user_id, self.demographics_data)
            self.error_message = "Demographics saved successfully!"
            print(f"[DEMOGRAPHIC_STATE] Demographics data saved for user {self.user_id}.")
            return rx.redirect("/app/questionnaire")  # Navigate to questionnaire page
        except Exception as e:
            self.error_message = f"Failed to save demographics: {str(e)}"
            print(f"[DEMOGRAPHIC_STATE] Error saving demographics: {e}")

    # Method to allow AuthState to trigger data loading without direct UI interaction
    # This is useful if the demographics page is visited and user identity is already known.
    @rx.event
    def ensure_data_loaded_for_user(self):
        if self.user_id and not self.demographics_data:
            print(
                f"[DEMOGRAPHIC_STATE] ensure_data_loaded_for_user: User ID {self.user_id} present, data empty. Attempting load."
            )
            self._load_demographics_from_firebase()
        elif not self.user_id:
            print("[DEMOGRAPHIC_STATE] ensure_data_loaded_for_user: No User ID.")
        else:
            print("[DEMOGRAPHIC_STATE] ensure_data_loaded_for_user: Data already present or User ID missing.")

    # Removed individual state variables:
    # gender: Optional[str] = None
    # onset_of_illness_years: Optional[str] = ""
    # education_level: Optional[str] = None
    # occupation: Optional[str] = None
    # has_psychiatric_history: Optional[str] = None
    # past_diagnoses: List[str] = [] # Now handled within demographics_data
    # onset_of_diagnosis_details: Optional[str] = ""
    # on_psychiatric_medication: Optional[str] = None
    # in_psychological_counseling: Optional[str] = None

    # Removed individual setter methods:
    # def handle_past_diagnoses(self, diagnosis: str, checked: bool): ...
    # def set_gender(self, gender: str): ...
    # def set_onset_of_illness_years(self, years: str): ...
    # def set_education_level(self, level: str): ...
    # def set_occupation(self, occupation: str): ...
    # def set_has_psychiatric_history(self, history: str): ...
    # def set_onset_of_diagnosis_details(self, details: str): ...
    # def set_on_psychiatric_medication(self, medication: str): ...
    # def set_in_psychological_counseling(self, counseling: str): ...

    # Removed submit_demographics as it's replaced by handle_submit


# Example of how to display the submitted data (could be on another page or part of the UI)
# def display_submitted_data() -> rx.Component:
#     return rx.vstack(
#         rx.heading("Submitted Demographic Data"),
#         rx.text(DemographicState.demographics_data.to_string()) # .to_string() is useful for dicts
#     )
