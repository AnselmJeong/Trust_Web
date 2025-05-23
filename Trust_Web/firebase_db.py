"""
This file is used to configure the Firebase DB, for saving and retrieving
experiment data.
"""
from pathlib import Path
from typing import Dict, Any, List, Optional
from google.cloud import firestore
# from google.cloud.firestore_v1.types import DatetimeWithNanoseconds as FirestoreDatetime # Removed this problematic import
from datetime import datetime # Standard datetime
from google.oauth2 import service_account
from dotenv import load_dotenv
import traceback # For detailed error logging
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
    if not doc_snapshot.exists:
        return None
    data = doc_snapshot.to_dict()
    if data is None: # Ensure data is not None before processing
        return None
    # Recursively convert all datetime-like objects in the document data
    processed_data = {key: _convert_value(value) for key, value in data.items()}
    return {
        "id": doc_snapshot.id, 
        "path": doc_snapshot.reference.path, 
        "data": processed_data
    }

def save_experiment_data(user_id: str, data: Dict[str, Any], doc_id: Optional[str] = None) -> None:
    """Save experiment data to Firestore in a hierarchical structure as described by the user."""
    try:
        print(f"user_id: {user_id}")
        if not user_id:
            raise ValueError("user_id is required to associate data with a user.")
        if "game_name" not in data:
            raise ValueError("game_name is required in data.")
        game_name = data["game_name"]
        if "timestamp" in data:
            del data["timestamp"]
        # Use a new dictionary for Firestore to avoid modifying the input `data` if it contains non-serializable types directly
        firestore_data = _convert_value(data.copy()) # Ensure data is serializable before saving
        firestore_data["timestamp"] = firestore.SERVER_TIMESTAMP

        # Top-level: IDs collection, user_id document
        user_doc_ref = db.collection("IDs").document(user_id)

        # --- Public Goods Game ---
        if game_name == "public goods game":
            round_num = firestore_data.get("round")
            if round_num is None:
                raise ValueError("'round' is required for public goods game data.")
            subcol = user_doc_ref.collection("public_goods_game")
            doc_ref = subcol.document(f"round_{round_num}")
            doc_ref.set(firestore_data)
            print(f"[Firestore] Saved public_goods_game/round_{round_num} for user {user_id}")
            return

        # --- Trust Game ---
        elif game_name == "trust game":
            section_num = firestore_data.get("section_num")
            stage_num = firestore_data.get("stage_num")
            round_num = firestore_data.get("round")
            if section_num is None:
                raise ValueError("'section_num' is required for trust game data.")
            trust_col = user_doc_ref.collection("trust_game")
            section_doc = trust_col.document(f"section{section_num}")
            if stage_num is not None and round_num is not None:
                stage_col = section_doc.collection(f"stage_{stage_num}")
                doc_ref = stage_col.document(f"round_{round_num}")
                doc_ref.set(firestore_data)
                print(f"[Firestore] Saved trust_game/section{section_num}/stage_{stage_num}/round_{round_num} for user {user_id}")
                return
            elif round_num is not None:
                doc_ref = section_doc.collection("rounds").document(f"round_{round_num}")
                doc_ref.set(firestore_data)
                print(f"[Firestore] Saved trust_game/section{section_num}/rounds/round_{round_num} for user {user_id}")
                return
            else:
                section_doc.set(firestore_data)
                print(f"[Firestore] Saved trust_game/section{section_num} for user {user_id}")
                return

        # --- Questionnaire ---
        elif game_name == "questionnaire_result":
            q_name = firestore_data.get("questionnaire_name")
            if not q_name:
                raise ValueError("'questionnaire_name' is required for questionnaire_result data.")
            subcol = user_doc_ref.collection("questionnaire")
            doc_ref = subcol.document(q_name)
            doc_ref.set(firestore_data)
            print(f"[Firestore] Saved questionnaire/{q_name} for user {user_id}")
            return

        # --- Demographics ---
        elif game_name == "demographics_data":
            subcol = user_doc_ref.collection("basic_info")
            doc_ref = subcol.document("demographic_data")
            # Remove game_name from data since it's not needed for demographics
            if "game_name" in firestore_data:
                del firestore_data["game_name"]
            doc_ref.set(firestore_data)
            print(f"[Firestore] Saved basic_info/demographic_data for user {user_id}")
            return

        # --- Fallback: flat save (legacy or unknown type) ---
        else:
            print(f"[Firestore][WARNING] Unknown game_name '{game_name}', saving flat under user doc.")
            user_doc_ref.collection("misc").add(firestore_data)
            return
    except ValueError as e:
        print(f"Validation error: {e}")
        raise
    except Exception as e:
        print(f"Error saving data to Firestore: {e}")
        raise


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


def get_user_experiment_data(user_id: str, game_name: str) -> List[Dict[str, Any]]:
    """
    Get all experiment data for a specific user and game by recursively fetching
    all documents from all subcollections under IDs/{user_id}/{game_name}.
    Converts Firestore timestamps to ISO strings.
    """
    all_docs_data: List[Dict[str, Any]] = []
    if not user_id:
        print("User ID not provided, cannot fetch experiment data.")
        return []
    if not game_name: # Check if game_name is provided
        print("Game name not provided, cannot fetch specific experiment data.")
        return []

    print(f"[DEBUG] Retrieving data for user: {user_id}, game: {game_name}")
    user_doc_ref = db.collection("IDs").document(user_id)
    # Target the specific game subcollection
    game_collection_ref = user_doc_ref.collection(game_name) 

    # Recursive helper function to fetch data from a reference (collection or document)
    def fetch_from_ref(current_ref):
        if isinstance(current_ref, firestore.CollectionReference):
            for doc_snapshot in current_ref.stream():
                doc_data = _process_doc_snapshot(doc_snapshot)
                if doc_data:
                    all_docs_data.append(doc_data)
                # Recursively fetch from subcollections of the current document
                for sub_coll_ref in doc_snapshot.reference.collections():
                    fetch_from_ref(sub_coll_ref)
        elif isinstance(current_ref, firestore.DocumentReference):
            # This case handles if we are passed a DocumentReference directly (e.g. a specific round doc).
            # Fetch its subcollections.
            # Also fetch the document itself if it has data.
            doc_data = _process_doc_snapshot(current_ref.get()) # Process the document itself
            if doc_data: # Ensure it's not already added to avoid duplicates if streamed from parent collection
                # Check for duplicates based on path before appending
                if not any(d["path"] == doc_data["path"] for d in all_docs_data):
                    all_docs_data.append(doc_data)
            for sub_coll_ref in current_ref.collections():
                fetch_from_ref(sub_coll_ref)

    try:
        # Start fetching from the specified game_collection_ref
        fetch_from_ref(game_collection_ref)
        
        print(f"[DEBUG] Fetched {len(all_docs_data)} documents for user {user_id}, game: {game_name}")
        return all_docs_data
    except Exception as e:
        print(f"Error fetching user experiment data for {user_id}, game: {game_name}: {e}")
        print(traceback.format_exc()) # Print full traceback
        return []


def get_experiment_statistics() -> Dict[str, Any]:
    """Get aggregated statistics for all experiment data from all user collections."""
    try:
        stats = {
            "total_documents_processed": 0,
            "distinct_users_with_data": 0,
            # Initialize other stats as needed. Note: amount_sent/returned might be tricky
            # with the new recursive get_user_experiment_data unless we specifically parse paths.
        }
        user_ids_with_data = set()
        
        ids_collection_ref = db.collection("IDs")
        for user_doc_snapshot in ids_collection_ref.stream(): # Iterate through all user docs in IDs collection
            user_id = user_doc_snapshot.id
            # For each user, you could call get_user_experiment_data, but that might be inefficient if you only need counts.
            # Or, more simply, count documents within known subcollection paths if stats are specific.
            # For now, let's just count users and total documents under them using a light scan.
            user_has_data = False
            for subcollection_ref in user_doc_snapshot.reference.collections():
                # Check if any subcollection has at least one document
                # For a more accurate doc count, would need to stream docs in each subcollection
                docs_in_subcollection = list(subcollection_ref.limit(1).stream())
                if docs_in_subcollection:
                    user_has_data = True
                    # This is a rough estimate of documents, not a full recursive count for stats.
                    # stats["total_documents_processed"] += len(list(subcollection_ref.stream())) # Potentially expensive
                    pass # Add more detailed counting if necessary for specific stats
            
            if user_has_data:
                user_ids_with_data.add(user_id)
        
        stats["distinct_users_with_data"] = len(user_ids_with_data)
        # To get total_documents, a full recursive scan like in get_user_experiment_data would be needed per user,
        # or a distributed counter if performance is critical for very large datasets.
        # For simplicity, total_documents is not accurately calculated here yet.
        print(f"Calculated experiment statistics: {stats}")
        return stats
    except Exception as e:
        print(f"Error fetching experiment statistics: {e}")
        print(traceback.format_exc())
        raise


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
