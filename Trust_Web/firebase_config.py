from google.cloud import firestore
from google.cloud.firestore import Client, DocumentReference, CollectionReference
from dotenv import load_dotenv
import requests
import os
from typing import Any, Dict, Optional, List
from google.oauth2 import service_account

# Load environment variables
load_dotenv()

# Get the path to the service account key file
credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if not credentials_path:
    raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set")

# Initialize Firestore client with credentials
try:
    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    db: Client = firestore.Client(credentials=credentials)
except Exception as e:
    print(f"Error initializing Firestore: {e}")
    raise

# Get Firebase configuration from environment variables
FIREBASE_CONFIG = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID"),
    "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID"),
}

# Verify all required Firebase configuration is present
for key, value in FIREBASE_CONFIG.items():
    if not value:
        raise ValueError(f"Missing required Firebase configuration: {key}")

# Firebase Web API Key for authentication
FIREBASE_API_KEY: str = FIREBASE_CONFIG["apiKey"]


def sign_in_with_email_and_password(email: str, password: str) -> Dict[str, Any]:
    """Sign in with email and password using Firebase Authentication REST API.

    Args:
        email: User's email address
        password: User's password

    Returns:
        Dictionary containing user data and ID token

    Raises:
        Exception: If authentication fails
    """
    try:
        # Verify the credentials using Firebase REST API
        sign_in_url: str = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
        sign_in_data: Dict[str, Any] = {
            "email": email,
            "password": password,
            "returnSecureToken": True,
        }

        response: requests.Response = requests.post(sign_in_url, json=sign_in_data)
        response.raise_for_status()  # Raise exception for bad status codes

        # Return the user data and tokens
        return response.json()

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            error_data: Dict[str, Any] = e.response.json()
            error_message: str = error_data.get("error", {}).get("message", "Authentication failed")
            if "INVALID_PASSWORD" in error_message:
                raise Exception("Invalid password")
            elif "EMAIL_NOT_FOUND" in error_message:
                raise Exception("User not found")
            else:
                raise Exception(f"Authentication error: {error_message}")
        raise Exception(f"Authentication error: {str(e)}")
    except Exception as e:
        raise Exception(f"Authentication error: {str(e)}")


def create_user_with_email_and_password(email: str, password: str) -> Dict[str, Any]:
    """Create a new user with email and password using Firebase REST API.

    Args:
        email: User's email address
        password: User's password

    Returns:
        Dictionary containing user data

    Raises:
        Exception: If user creation fails
    """
    try:
        # Create user using Firebase REST API
        sign_up_url: str = (
            f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
        )
        sign_up_data: Dict[str, Any] = {
            "email": email,
            "password": password,
            "returnSecureToken": True,
        }

        response: requests.Response = requests.post(sign_up_url, json=sign_up_data)
        response.raise_for_status()

        return response.json()

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            error_data: Dict[str, Any] = e.response.json()
            error_message: str = error_data.get("error", {}).get("message", "User creation failed")
            raise Exception(f"Error creating user: {error_message}")
        raise Exception(f"Error creating user: {str(e)}")
    except Exception as e:
        raise Exception(f"Error creating user: {str(e)}")


def save_experiment_data(data: Dict[str, Any]) -> None:
    """Save experiment data to Firestore in user-specific subcollection.

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

        # Get the users collection and specific user document
        users_ref: CollectionReference = db.collection("users")
        user_doc: DocumentReference = users_ref.document(user_id)

        # Get the experiments subcollection for this user
        experiments_ref: CollectionReference = user_doc.collection("experiments")

        # Add timestamp if not present
        if "timestamp" not in data:
            data["timestamp"] = firestore.SERVER_TIMESTAMP

        # Create a new document with auto-generated ID in the user's experiments subcollection
        doc_ref: DocumentReference = experiments_ref.document()

        # Save to Firestore
        doc_ref.set(data)

    except ValueError as e:
        print(f"Validation error: {e}")
        raise
    except Exception as e:
        print(f"Error saving data to Firestore: {e}")
        raise


def get_user_experiment_data(user_id: str) -> List[Dict[str, Any]]:
    """Get all experiment data for a specific user from their subcollection.

    Args:
        user_id: The user's ID to fetch data for

    Returns:
        List of experiment data documents

    Raises:
        Exception: If fetching data fails
    """
    try:
        # Get the user's experiments subcollection
        user_doc: DocumentReference = db.collection("users").document(user_id)
        experiments_ref: CollectionReference = user_doc.collection("experiments")

        # Get all documents in the subcollection
        docs = experiments_ref.stream()

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
        # Get the users collection
        users_ref: CollectionReference = db.collection("users")

        # Initialize statistics
        stats = {
            "total_experiments": 0,
            "total_users": 0,
            "total_amount_sent": 0,
            "total_amount_returned": 0,
        }

        # Get all users
        users = users_ref.stream()

        # Process each user's experiments
        for user in users:
            stats["total_users"] += 1
            experiments_ref = user.reference.collection("experiments")
            experiments = experiments_ref.stream()

            for doc in experiments:
                data = doc.to_dict()
                stats["total_experiments"] += 1
                stats["total_amount_sent"] += data.get("amount_sent", 0)
                stats["total_amount_returned"] += data.get("amount_returned", 0)

        return stats

    except Exception as e:
        print(f"Error fetching experiment statistics: {e}")
        raise
