"""
This file is used to configure the Firebase API key and authentication
for user login and signup.
"""

from dotenv import load_dotenv
import requests
import os
from typing import Any, Dict

# Load environment variables
load_dotenv()

# Get Firebase API Key for authentication
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")
if not FIREBASE_API_KEY:
    raise ValueError("Missing required Firebase configuration: FIREBASE_API_KEY")


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
        sign_in_url: str = (
            f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
        )
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
        sign_up_url: str = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
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
