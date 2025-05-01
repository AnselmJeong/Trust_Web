import json
import os
from pathlib import Path
from typing import Dict, Any

def setup_firebase_credentials():
    """Set up Firebase credentials from service account JSON file."""
    # Check if .env file exists
    env_path = Path(".env")
    if env_path.exists():
        print(
            "Warning: .env file already exists. This will overwrite existing Firebase credentials."
        )
        response: str = input("Do you want to continue? (y/n): ")
        if response.lower() != "y":
            print("Setup cancelled.")
            return

    # Get the path to the service account JSON file
    json_path: str = input("Enter the path to your Firebase service account JSON file: ").strip()
    if not os.path.exists(json_path):
        print(f"Error: File not found at {json_path}")
        return

    try:
        # Read the JSON file
        with open(json_path, "r") as f:
            service_account: Dict[str, Any] = json.load(f)

        # Create .env content
        env_content: str = f"""# Firebase Configuration
            FIREBASE_PROJECT_ID={service_account["project_id"]}
            FIREBASE_PRIVATE_KEY_ID={service_account["private_key_id"]}
            FIREBASE_PRIVATE_KEY="{service_account["private_key"]}"
            FIREBASE_CLIENT_EMAIL={service_account["client_email"]}
            FIREBASE_CLIENT_ID={service_account["client_id"]}
            FIREBASE_CLIENT_CERT_URL={service_account["client_x509_cert_url"]}
            """

        # Write to .env file
        with open(".env", "w") as f:
            f.write(env_content)

        print("Firebase credentials have been successfully set up in .env file.")
        print("Make sure to add .env to your .gitignore file to keep your credentials secure.")

    except Exception as e:
        print(f"Error setting up credentials: {e}")


if __name__ == "__main__":
    setup_firebase_credentials()
