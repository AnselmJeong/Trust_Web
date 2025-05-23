"""
This file is used to configure the Firebase DB, for saving and retrieving
experiment data.
"""
from pathlib import Path
from typing import Dict, Any, List, Optional
from google.cloud import firestore
# from google.cloud.firestore_v1.types import Timestamp # Removed problematic import
from datetime import datetime # Standard datetime
from google.oauth2 import service_account
from dotenv import load_dotenv
import traceback # For detailed error logging
# from Trust_Web.firebase_config import app_env # Removed this import as FIREBASE_ENABLED checks are removed
# from Trust_Web.authentication import AuthState

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

# Helper function to convert datetime objects to ISO strings
# and recursively process nested dicts/lists.
def _convert_value(value):
    # Removed FirestoreDatetime check, relying on standard datetime
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: _convert_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_convert_value(item) for item in value]
    return value

# Helper function to process a document snapshot
def _process_doc_snapshot(doc_snapshot):
    if doc_snapshot:
        processed_data = {key: _convert_value(value) for key, value in doc_snapshot.items()}
    else:
        processed_data = {}
    return processed_data

def save_experiment_data(user_id: str, data: dict, game_name: str = None, section_num: int = None, document_id: str = None) -> None:
    """
    Saves experiment data to Firestore.
    Can save to a top-level game collection, a subcollection within a game (e.g., 'section1'),
    and can specify a document ID or allow Firestore to auto-generate one.
    """
    # if not app_env.FIREBASE_ENABLED:
    #     print("[SAVE_EXPERIMENT_DATA] Firebase is not enabled. Skipping save.")
    #     return
    try:
        user_doc_ref = db.collection("IDs").document(user_id)
        
        # Determine the target collection reference
        if game_name:
            game_doc_ref = user_doc_ref.collection(game_name)
            if game_name == "trust_game" and section_num:
                target_collection_ref = game_doc_ref.document(f"section{section_num}").collection("rounds")
            else:
                # If no section_collection, save directly under the game_name collection
                target_collection_ref = game_doc_ref
        else:
            # Fallback if no game_name, save directly under user_id (e.g., demographics)
            target_collection_ref = user_doc_ref

        # Add server timestamp
        data_to_save = _process_doc_snapshot(data) # Convert datetimes etc.
        data_to_save["saved_at"] = firestore.SERVER_TIMESTAMP

        if document_id:
            doc_ref = target_collection_ref.document(document_id)
            doc_ref.set(data_to_save, merge=True)
            print(f"[SAVE_EXPERIMENT_DATA] Data saved to: {doc_ref.path}")
        else:
            # Auto-generate document ID
            doc_ref = target_collection_ref.add(data_to_save)
            print(f"[SAVE_EXPERIMENT_DATA] Data saved with auto-ID: {doc_ref[1].path}")

    except Exception as e:
        print(f"Error saving experiment data for user {user_id}, game {game_name}, section {section_num}, doc {document_id}: {e}")
        # Optionally, re-raise the exception or handle it as per application's error handling policy
        # raise

def get_user_experiment_data(user_id: str, game_name: str, section_num: int = 1) -> list:
    """
    Fetches all experiment data for a specific game for a given user.
    For 'trust_game', it fetches section 1 summary and its rounds.
    """
    # if not app_env.FIREBASE_ENABLED:
    #     print("[GET_USER_EXPERIMENT_DATA] Firebase is not enabled. Skipping fetch.")
    #     return [{"error": "Firebase not enabled"}]
    try:
        data_list = []

        if game_name == "public_goods_game":
            game_collection_ref = db.collection("IDs").document(user_id).collection("public_goods_game")
            docs = game_collection_ref.stream()
            for doc in docs:
                processed_doc = _process_doc_snapshot(doc.to_dict())
                data_list.append({"id": doc.id, "data": processed_doc})
            print(f"[GET_USER_EXPERIMENT_DATA] Fetched {len(data_list)} documents for {game_name} for user {user_id}")
        
        elif game_name == "trust_game":
            game_collection_ref = db.collection("IDs").document(user_id).collection("trust_game")
            if section_num == 1:
                rounds_collection_ref = game_collection_ref.document("section1").collection("rounds")
                round_docs = rounds_collection_ref.stream()
                for doc in round_docs:
                    processed_doc = _convert_value(doc.to_dict())
                    data_list.append({"id": doc.id, "data": processed_doc})
            elif section_num == 2:
                rounds_collection_ref = game_collection_ref.document("section2").collection("rounds")
                round_docs = rounds_collection_ref.stream()
                for doc in round_docs:
                    processed_doc = _convert_value(doc.to_dict())
                    data_list.append({"id": doc.id, "data": processed_doc})
            print(f"[GET_USER_EXPERIMENT_DATA] Fetched {len(data_list)} documents for {game_name} {section_num} for user {user_id}")
    
        else:
            # Generic fetch for other game types or data (e.g., questionnaires, demographics)
            # This assumes these are stored directly as documents in a collection named game_name
            # under the user's ID.
            top_level_collection_ref = db.collection("IDs").document(user_id).collection(game_name)
            docs = top_level_collection_ref.stream()
            for doc in docs:
                processed_doc = _process_doc_snapshot(doc.to_dict())
                data_list.append({"id": doc.id, "data": processed_doc})
            if not data_list: # Check if still empty, maybe it's a single document not a collection
                doc_ref = db.collection("IDs").document(user_id).get() # this path is wrong, should be IDs/user_id/game_name (document)
                if doc_ref and game_name in doc_ref.to_dict():
                     processed_doc = _process_doc_snapshot(doc_ref.to_dict()[game_name]) # this is also probably wrong
                     data_list.append({"id": game_name, "data": processed_doc})

            print(f"[GET_USER_EXPERIMENT_DATA] Fetched {len(data_list)} documents for generic game/data type '{game_name}' for user {user_id}")


        if not data_list:
            print(f"[GET_USER_EXPERIMENT_DATA] No data found for user {user_id}, game_name: {game_name}")
        
        return data_list

    except Exception as e:
        print(f"Error fetching experiment data for user {user_id}, game {game_name}: {e}")
        return [{"error_fetching": str(e)}]

def get_user_questionnaire_responses(user_id: str) -> Dict[str, Dict[str, Any]]:
    """Fetches all questionnaire responses for a user from their new structure."""
    try:
        if not user_id:
            print("User ID not provided, cannot fetch questionnaire responses.")
            return {}
        
        user_doc_ref = db.collection("IDs").document(user_id)
        subcol = user_doc_ref.collection("questionnaire")
        docs = subcol.stream()
        responses = {}
        for doc in docs:
            processed_doc = _process_doc_snapshot(doc) # Process for timestamps
            if processed_doc and processed_doc["data"]:
                q_name = processed_doc["id"]
                responses[q_name] = {"doc_id": q_name, "data": processed_doc["data"]}
        print(f"Fetched questionnaire responses for user {user_id}: {list(responses.keys())}")
        return responses
    except Exception as e:
        print(f"Error fetching questionnaire responses for user {user_id}: {e}")
        return {}

# def get_experiment_statistics() -> Dict[str, Any]:
#     """Get aggregated statistics for all experiment data from all user collections."""
#     try:
#         stats = {
#             "total_documents_processed": 0,
#             "distinct_users_with_data": 0,
#             # Initialize other stats as needed. Note: amount_sent/returned might be tricky
#             # with the new recursive get_user_experiment_data unless we specifically parse paths.
#         }
#         user_ids_with_data = set()
        
#         ids_collection_ref = db.collection("IDs")
#         for user_doc_snapshot in ids_collection_ref.stream(): # Iterate through all user docs in IDs collection
#             user_id = user_doc_snapshot.id
#             # For each user, you could call get_user_experiment_data, but that might be inefficient if you only need counts.
#             # Or, more simply, count documents within known subcollection paths if stats are specific.
#             # For now, let's just count users and total documents under them using a light scan.
#             user_has_data = False
#             for subcollection_ref in user_doc_snapshot.reference.collections():
#                 # Check if any subcollection has at least one document
#                 # For a more accurate doc count, would need to stream docs in each subcollection
#                 docs_in_subcollection = list(subcollection_ref.limit(1).stream())
#                 if docs_in_subcollection:
#                     user_has_data = True
#                     # This is a rough estimate of documents, not a full recursive count for stats.
#                     # stats["total_documents_processed"] += len(list(subcollection_ref.stream())) # Potentially expensive
#                     pass # Add more detailed counting if necessary for specific stats
            
#             if user_has_data:
#                 user_ids_with_data.add(user_id)
        
#         stats["distinct_users_with_data"] = len(user_ids_with_data)
#         # To get total_documents, a full recursive scan like in get_user_experiment_data would be needed per user,
#         # or a distributed counter if performance is critical for very large datasets.
#         # For simplicity, total_documents is not accurately calculated here yet.
#         print(f"Calculated experiment statistics: {stats}")
#         return stats
#     except Exception as e:
#         print(f"Error fetching experiment statistics: {e}")
#         print(traceback.format_exc())
#         raise

def get_user_demographics_data(user_id: str) -> Optional[Dict[str, Any]]:
    """Fetches the demographic data for a user from their new structure."""
    try:
        if not user_id:
            print("User ID not provided, cannot fetch demographic data.")
            return None
        user_doc_ref = db.collection("IDs").document(user_id)
        subcol = user_doc_ref.collection("basic_info")
        doc_snapshot = subcol.document("demographic_data").get()
        
        processed_doc = _process_doc_snapshot(doc_snapshot) # Process for timestamps
        if processed_doc and processed_doc["data"]:
            print(f"Fetched demographic data for user {user_id}, doc_id: {processed_doc['id']}")
            return {"doc_id": processed_doc["id"], "data": processed_doc["data"]}
        
        print(f"No demographic data found for user {user_id} or data was empty.")
        return None
    except Exception as e:
        print(f"Error fetching demographic data for user {user_id}: {e}")
        return None

def get_all_user_data_for_export(user_id: str) -> dict:
    pass
