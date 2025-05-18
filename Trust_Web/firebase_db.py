"""
This file is used to configure the Firebase DB, for saving and retrieving
experiment data.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from google.cloud import firestore
from google.oauth2 import service_account
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# Initialize Firestore client
def init_firebase_client() -> firestore.Client:
    """Initialize and return Firestore client with credentials."""
    credentials_path = Path(__file__).parent.parent / "secret" / "trustweb.json"
    print(credentials_path)

    try:
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        return firestore.Client(credentials=credentials)
    except Exception as e:
        print(f"Error initializing Firestore: {e}")
        raise


# Initialize the client
db = init_firebase_client()

COLLECTION_NAME = "trust_experiment"  # Define the global collection name


def save_experiment_data(
    user_local_id: str, data: Dict[str, Any], doc_id: Optional[str] = None
) -> None:
    """Save or update experiment data to Firestore in a global collection.

    Args:
        user_local_id: The Firebase user ID (localId) to be stored as a field in the document.
        data: Dictionary containing experiment data to save. Should include 'user_email'.
        doc_id: Optional. If provided, updates the document with this ID. Otherwise, creates a new document.

    Raises:
        ValueError: If user_local_id is not provided.
        Exception: If saving data fails
    """
    try:
        if not user_local_id:
            raise ValueError("user_local_id is required to associate data with a user.")

        # Store the user's localId as a field within the data
        data["user_id_local"] = user_local_id

        target_collection = db.collection(COLLECTION_NAME)

        data["timestamp"] = firestore.SERVER_TIMESTAMP

        if "user_email" not in data:
            print("Warning: 'user_email' not found in data being saved to Firestore.")

        if doc_id:
            doc_ref = target_collection.document(doc_id)
            doc_ref.set(
                data, merge=True
            )  # Use merge=True if you want to update fields, not overwrite
            print(f"Data updated in Firestore collection {COLLECTION_NAME}, doc {doc_id}")
        else:
            doc_ref = target_collection.document()
            doc_ref.set(data)
            print(f"Data saved to Firestore collection {COLLECTION_NAME}, new doc ID: {doc_ref.id}")

    except ValueError as e:
        print(f"Validation error: {e}")
        raise
    except Exception as e:
        print(f"Error saving data to Firestore: {e}")
        raise


def get_user_questionnaire_responses(user_local_id: str) -> Dict[str, Dict[str, Any]]:
    """
    Fetches the most recent questionnaire responses for a user from the global collection.
    Each questionnaire type will have at most one entry (the latest).

    Args:
        user_local_id: The Firebase user ID (localId) to filter by.

    Returns:
        A dictionary where keys are questionnaire names (e.g., "UCLA")
        and values are dicts containing 'doc_id', 'responses', and 'timestamp'.
        Returns an empty dict if no data or an error occurs.
    """
    try:
        if not user_local_id:
            print("User local ID not provided, cannot fetch questionnaire responses.")
            return {}

        target_collection = db.collection(COLLECTION_NAME)
        query = (
            target_collection.where(
                filter=firestore.FieldFilter("user_id_local", "==", user_local_id)
            )
            .where(filter=firestore.FieldFilter("type", "==", "questionnaire_result"))
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
        )

        docs = query.stream()

        latest_responses: Dict[str, Dict[str, Any]] = {}
        for doc in docs:
            data = doc.to_dict()
            if data:  # Ensure data is not None
                q_name = data.get("questionnaire_name")
                # If we haven't stored an entry for this questionnaire_name yet, this is the latest one
                if q_name and q_name not in latest_responses:
                    doc_responses = data.get("responses")
                    if isinstance(doc_responses, list):  # Basic validation
                        latest_responses[q_name] = {
                            "doc_id": doc.id,
                            "responses": doc_responses,
                            "timestamp": data.get("timestamp"),  # Store timestamp for reference
                        }
                    else:
                        print(
                            f"Warning: Responses for {q_name} (doc: {doc.id}) are not in expected list format: {doc_responses}"
                        )

        print(
            f"Fetched questionnaire responses for user {user_local_id}: {latest_responses.keys()}"
        )
        return latest_responses
    except Exception as e:
        print(f"Error fetching questionnaire responses for user {user_local_id}: {e}")
        return {}


def get_user_experiment_data(user_local_id: str) -> List[Dict[str, Any]]:
    """Get all experiment data for a specific user from the global collection.

    Args:
        user_local_id: The user's local ID to fetch data for.

    Returns:
        List of experiment data documents.

    Raises:
        Exception: If fetching data fails.
    """
    try:
        if not user_local_id:
            print("User local ID not provided, cannot fetch experiment data.")
            return []

        target_collection = db.collection(COLLECTION_NAME)
        query = target_collection.where(
            filter=firestore.FieldFilter("user_id_local", "==", user_local_id)
        )
        docs = query.stream()

        return [doc.to_dict() for doc in docs if doc.exists]
    except Exception as e:
        print(f"Error fetching user experiment data for {user_local_id}: {e}")
        return []


def get_experiment_statistics() -> Dict[str, Any]:
    """Get aggregated statistics for all experiment data from the global collection.

    Returns:
        Dictionary containing experiment statistics.

    Raises:
        Exception: If fetching statistics fails.
    """
    try:
        stats = {
            "total_documents": 0,  # Changed from total_experiments
            "distinct_users": 0,
            "total_amount_sent": 0,
            "total_amount_returned": 0,
        }

        target_collection = db.collection(COLLECTION_NAME)
        docs = target_collection.stream()

        user_ids_seen = set()

        for doc in docs:
            data = doc.to_dict()
            if data:
                stats["total_documents"] += 1
                user_id = data.get("user_id_local")
                if user_id:
                    user_ids_seen.add(user_id)

                # Example: Summing specific fields if they exist and are numbers
                if (
                    data.get("type") != "questionnaire_result"
                ):  # Avoid double counting if structures differ
                    stats["total_amount_sent"] += data.get("amount_sent", 0)
                    stats["total_amount_returned"] += data.get("amount_returned", 0)

        stats["distinct_users"] = len(user_ids_seen)
        return stats

    except Exception as e:
        print(f"Error fetching experiment statistics: {e}")
        raise
