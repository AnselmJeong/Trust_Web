"""
This file is used to configure the Firebase DB, for saving and retrieving
experiment data.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from google.cloud import firestore

# from google.cloud.firestore_v1.types import Timestamp # Removed problematic import
from datetime import datetime  # Standard datetime
from google.oauth2 import service_account
from dotenv import load_dotenv
import traceback  # For detailed error logging
# from Trust_Web.firebase_config import app_env # Removed this import as FIREBASE_ENABLED checks are removed
# from Trust_Web.authentication import AuthState # Removed unused import

# Load environment variables
load_dotenv()


# Initialize Firestore client
def init_firebase_client() -> firestore.Client:
    """Initialize and return Firestore client with credentials."""
    credentials_path = Path(__file__).parent.parent / "secret" / "trustweb.json"
    print(credentials_path)

    try:
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path
        )
        return firestore.Client(credentials=credentials)
    except Exception as e:
        print(f"Error initializing Firestore: {e}")
        raise


# Initialize the client
db = init_firebase_client()

# --- Firestore Collection and Document Names ---
USERS_COLLECTION = "IDs"
TRUST_GAME_COLLECTION = "trust_game"
ROUNDS_SUBCOLLECTION = "rounds"
QUESTIONNAIRE_COLLECTION = "questionnaire"
BASIC_INFO_COLLECTION = "basic_info"
DEMOGRAPHICS_DOC = "demographic_data"
PUBLIC_GOODS_GAME_COLLECTION = "public_goods_game"
SECTION_DOC_PREFIX = "section"
# --- End Firestore Names ---

# --- Path Helper Functions ---
def _get_user_doc_ref(user_id: str) -> firestore.DocumentReference:
    """Returns the document reference for a given user."""
    return db.collection(USERS_COLLECTION).document(user_id)

def _get_game_collection_ref(user_id: str, game_name: str) -> firestore.CollectionReference:
    """Returns the collection reference for a given game under a user."""
    return _get_user_doc_ref(user_id).collection(game_name)

def _get_trust_game_section_rounds_collection_ref(user_id: str, section_num: int) -> firestore.CollectionReference:
    """Returns the rounds collection reference for a specific section of the trust game."""
    if not isinstance(section_num, int): # Ensure section_num is an int for path construction
        raise TypeError(f"section_num must be an integer, got {type(section_num)}")
    return _get_game_collection_ref(user_id, TRUST_GAME_COLLECTION).document(f"{SECTION_DOC_PREFIX}{section_num}").collection(ROUNDS_SUBCOLLECTION)

def _get_questionnaire_collection_ref(user_id: str) -> firestore.CollectionReference:
    """Returns the collection reference for questionnaires under a user."""
    return _get_user_doc_ref(user_id).collection(QUESTIONNAIRE_COLLECTION)

def _get_demographics_doc_ref(user_id: str) -> firestore.DocumentReference:
    """Returns the document reference for demographic_data under basic_info for a user."""
    return _get_user_doc_ref(user_id).collection(BASIC_INFO_COLLECTION).document(DEMOGRAPHICS_DOC)
# --- End Path Helper Functions ---


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
# Always returns a dict with 'id' and 'data' keys for compatibility
def _process_doc_snapshot(doc_snapshot):
    # If it's a Firestore DocumentSnapshot (has .id and .to_dict())
    if hasattr(doc_snapshot, "id") and hasattr(doc_snapshot, "to_dict"):
        data = doc_snapshot.to_dict()
        processed_data = (
            {key: _convert_value(value) for key, value in data.items()} if data else {}
        )
        return {"id": doc_snapshot.id, "data": processed_data}
    # If it's already a dict (e.g., from .to_dict()), wrap it
    elif isinstance(doc_snapshot, dict):
        processed_data = (
            {key: _convert_value(value) for key, value in doc_snapshot.items()}
            if doc_snapshot
            else {}
        )
        return {"id": None, "data": processed_data}
    # If None or unknown type, return empty
    else:
        return {"id": None, "data": {}}


def save_experiment_data(
    user_id: str,
    game_name: str, # Made game_name mandatory
    data: dict,
    section_num: Optional[int] = None,
    document_id: Optional[str] = None,
) -> None:
    """
    Saves experiment data to a specified collection in Firestore.

    Args:
        user_id: The ID of the user.
        game_name: The name of the game or data category (e.g., "trust_game", "public_goods_game", "questionnaire", "basic_info").
                   This will correspond to a collection under the user's document.
        data: The data dictionary to save.
        section_num: Optional. Required if game_name is "trust_game", to specify the section number.
        document_id: Optional. If provided, data will be saved to a document with this ID.
                       If None, Firestore will auto-generate a document ID.
    """
    # if not app_env.FIREBASE_ENABLED:
    #     print("[SAVE_EXPERIMENT_DATA] Firebase is not enabled. Skipping save.")
    #     return
    try:
        if not game_name:
            # This check is technically redundant if game_name is mandatory in signature,
            # but kept for robustness during refactoring or if signature changes.
            raise ValueError("game_name must be provided to save experiment data.")

        # Determine the target collection reference using helper functions
        if game_name == TRUST_GAME_COLLECTION:
            if section_num is None:
                raise ValueError(f"section_num is required for game_name '{TRUST_GAME_COLLECTION}'")
            target_collection_ref = _get_trust_game_section_rounds_collection_ref(user_id, section_num)
        else:
            # Covers PUBLIC_GOODS_GAME_COLLECTION, QUESTIONNAIRE_COLLECTION, BASIC_INFO_COLLECTION, etc.
            target_collection_ref = _get_game_collection_ref(user_id, game_name)
            if game_name == BASIC_INFO_COLLECTION and not document_id:
                # This warning is specific to how basic_info might be structured (usually one doc)
                print(f"Warning: Saving to '{game_name}' collection without a specific document_id. Data will have an auto-generated ID.")


        # Add server timestamp
        data_to_save = _convert_value(data)  # Process datetimes etc.
        data_to_save["saved_at"] = firestore.SERVER_TIMESTAMP # Use Firestore server timestamp

        if document_id:
            doc_ref = target_collection_ref.document(document_id)
            doc_ref.set(data_to_save, merge=True) # Use set with merge=True to create or update
            print(f"[SAVE_EXPERIMENT_DATA] Data saved to document: {doc_ref.path}")
        else:
            # Auto-generate document ID using .add()
            # .add() returns a tuple: (timestamp, DocumentReference)
            timestamp, doc_ref = target_collection_ref.add(data_to_save)
            print(f"[SAVE_EXPERIMENT_DATA] Data saved with auto-generated ID to document: {doc_ref.path} at {timestamp}")

    except Exception as e:
        # Improved error logging
        error_message = (
            f"Error saving experiment data for user_id='{user_id}', game_name='{game_name}', "
            f"section_num='{section_num}', document_id='{document_id}'. Error: {e}"
        )
        print(error_message)
        traceback.print_exc() # Print full traceback for debugging
        # Optionally, re-raise the exception or handle it as per application's error handling policy
        # raise e
        # Standardize error return for consistency (though not explicitly requested for this func, good practice)
        # return {"error_saving": str(e), "details": traceback.format_exc()} # Or raise


def get_user_experiment_data(
    user_id: str, game_name: str, section_num: int = 1
) -> list:
    """
    Fetches all experiment data for a specific game collection for a given user.
    For 'trust_game', it fetches data from the 'rounds' subcollection of the specified section.
    For other game_names, it fetches all documents from the collection named game_name.
    """
    # if not app_env.FIREBASE_ENABLED:
    #     print("[GET_USER_EXPERIMENT_DATA] Firebase is not enabled. Skipping fetch.")
    #     return [{"error": "Firebase not enabled"}]
    try:
        data_list = []
        collection_name_for_print = game_name # For logging purposes

        if game_name == TRUST_GAME_COLLECTION:
            # section_num is used by the helper, default is 1 from signature
            target_collection_ref = _get_trust_game_section_rounds_collection_ref(user_id, section_num)
            collection_name_for_print = f"{game_name}/{SECTION_DOC_PREFIX}{section_num}/{ROUNDS_SUBCOLLECTION}"
        elif game_name == PUBLIC_GOODS_GAME_COLLECTION:
            target_collection_ref = _get_game_collection_ref(user_id, PUBLIC_GOODS_GAME_COLLECTION)
        else:
            # Generic fetch for other game types (e.g., QUESTIONNAIRE_COLLECTION)
            target_collection_ref = _get_game_collection_ref(user_id, game_name)
        
        docs = target_collection_ref.stream()
        for doc in docs:
            processed_doc = _process_doc_snapshot(doc)
            data_list.append(processed_doc)

        # Fallback logic for when game_name might represent a document ID within a collection of the same name.
        # This is specific and kept for compatibility if such structures were used.
        if not data_list and game_name not in [TRUST_GAME_COLLECTION, PUBLIC_GOODS_GAME_COLLECTION]:
            try:
                single_doc_ref = _get_game_collection_ref(user_id, game_name).document(game_name).get()
                if single_doc_ref and single_doc_ref.exists:
                    processed_doc = _process_doc_snapshot(single_doc_ref)
                    data_list.append(processed_doc)
                    collection_name_for_print = f"{game_name}/{game_name} (single document)" 
            except Exception as e_single_doc:
                print(f"Note: Fallback attempt to fetch single document at '{game_name}/{game_name}' failed: {e_single_doc}")


        if data_list:
            print(
                f"[GET_USER_EXPERIMENT_DATA] Fetched {len(data_list)} document(s) for '{collection_name_for_print}' for user '{user_id}'"
            )
        else:
            print(
                f"[GET_USER_EXPERIMENT_DATA] No data found for user '{user_id}', path '{collection_name_for_print}'"
            )

        return data_list

    except Exception as e:
        # Consistent error logging
        error_message = (
            f"Error fetching experiment data for user_id='{user_id}', game_name='{game_name}', "
            f"section_num='{section_num}'. Error: {e}"
        )
        print(error_message)
        traceback.print_exc()
        return [{"error_fetching": str(e), "details": traceback.format_exc()}]


def get_user_questionnaire_responses(user_id: str) -> Dict[str, Dict[str, Any]]:
    """Fetches all questionnaire responses for a user."""
    try:
        if not user_id:
            print("[GET_USER_QUESTIONNAIRE_RESPONSES] User ID not provided.")
            return {}

        questionnaire_coll_ref = _get_questionnaire_collection_ref(user_id)
        docs = questionnaire_coll_ref.stream()
        responses = {}
        for doc in docs:
            processed_doc = _process_doc_snapshot(doc) # Ensures consistent processing
            if processed_doc and processed_doc["id"] and processed_doc["data"]: # Ensure id and data are present
                q_name = processed_doc["id"] # The document ID is the questionnaire name (e.g., "AQ")
                responses[q_name] = {"doc_id": q_name, "data": processed_doc["data"]}
        
        if responses:
            print(
                f"[GET_USER_QUESTIONNAIRE_RESPONSES] Fetched responses for questionnaires: {list(responses.keys())} for user '{user_id}'"
            )
        else:
            print(f"[GET_USER_QUESTIONNAIRE_RESPONSES] No questionnaire responses found for user '{user_id}'.")
        return responses
    except Exception as e:
        print(f"[GET_USER_QUESTIONNAIRE_RESPONSES] Error fetching responses for user '{user_id}': {e}")
        traceback.print_exc()
        return {"error_fetching": str(e), "details": traceback.format_exc()}

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
# def get_experiment_statistics() -> Dict[str, Any]:
# """Get aggregated statistics for all experiment data from all user collections."""
# ... (code for get_experiment_statistics remains unchanged for now) ...
#     except Exception as e:
#         print(f"Error fetching experiment statistics: {e}")
#         print(traceback.format_exc())
#         raise


def get_user_demographics_data(user_id: str) -> Optional[Dict[str, Any]]:
    """Fetches the demographic data for a user."""
    try:
        if not user_id:
            print("[GET_USER_DEMOGRAPHICS_DATA] User ID not provided.")
            return None

        demographics_doc_ref = _get_demographics_doc_ref(user_id)
        doc_snapshot = demographics_doc_ref.get()

        processed_doc = _process_doc_snapshot(doc_snapshot)
        if processed_doc and processed_doc["data"]: # Check if data exists after processing
            # The 'id' from _process_doc_snapshot will be 'demographic_data' if the doc exists
            print(
                f"[GET_USER_DEMOGRAPHICS_DATA] Fetched demographic data for user '{user_id}', doc_id: {processed_doc.get('id', 'N/A')}"
            )
            # Return in the same structure as other data getters if possible,
            # though this one is for a single known document.
            return {"doc_id": processed_doc.get("id"), "data": processed_doc["data"]}

        print(f"[GET_USER_DEMOGRAPHICS_DATA] No demographic data found for user '{user_id}'.")
        return None
    except Exception as e:
        print(f"[GET_USER_DEMOGRAPHICS_DATA] Error fetching data for user '{user_id}': {e}")
        traceback.print_exc()
        return {"error_fetching": str(e), "details": traceback.format_exc()}


def get_all_user_data_for_export(user_id: str) -> dict:
    pass
