"""
This file is used to configure the Firebase DB, for saving and retrieving
experiment data.
"""

from pathlib import Path
from typing import Dict, Any, List
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


def save_experiment_data(data: Dict[str, Any]) -> None:
    """Save experiment data to Firestore in user-specific collection.

    Args:
        data: Dictionary containing experiment data to save. Must include 'user_id'.

    Raises:
        ValueError: If user_id is not provided in data
        Exception: If saving data fails
    """
    try:
        # Check if user_id is provided
        user_id = data.get("user_id")
        if not user_id:
            raise ValueError("user_id is required in data")

        # Get the user's collection
        user_collection = db.collection(user_id)

        # Add timestamp if not present
        if "timestamp" not in data:
            data["timestamp"] = firestore.SERVER_TIMESTAMP

        # Create a new document with auto-generated ID
        doc_ref = user_collection.document()

        # Save to Firestore
        doc_ref.set(data)

    except ValueError as e:
        print(f"Validation error: {e}")
        raise
    except Exception as e:
        print(f"Error saving data to Firestore: {e}")
        raise


def get_user_experiment_data(user_id: str) -> List[Dict[str, Any]]:
    """Get all experiment data for a specific user.

    Args:
        user_id: The user's ID to fetch data for

    Returns:
        List of experiment data documents

    Raises:
        Exception: If fetching data fails
    """
    try:
        # Get the user's collection
        user_collection = db.collection(user_id)

        # Get all documents in the collection
        docs = user_collection.stream()

        # Convert to list of dictionaries
        return [doc.to_dict() for doc in docs]

    except Exception as e:
        print(f"Error fetching user experiment data: {e}")
        raise


def get_experiment_statistics() -> Dict[str, Any]:
    """Get aggregated statistics for all experiment data across all users.

    Returns:
        Dictionary containing experiment statistics

    Raises:
        Exception: If fetching statistics fails
    """
    try:
        # Initialize statistics
        stats = {
            "total_experiments": 0,
            "total_users": 0,
            "total_amount_sent": 0,
            "total_amount_returned": 0,
        }

        # Get all collections (each collection represents a user)
        collections = db.collections()

        # Process each user's collection
        for collection in collections:
            stats["total_users"] += 1
            docs = collection.stream()

            for doc in docs:
                data = doc.to_dict()
                stats["total_experiments"] += 1
                stats["total_amount_sent"] += data.get("amount_sent", 0)
                stats["total_amount_returned"] += data.get("amount_returned", 0)

        return stats

    except Exception as e:
        print(f"Error fetching experiment statistics: {e}")
        raise
