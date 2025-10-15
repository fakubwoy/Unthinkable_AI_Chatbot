import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import datetime
import uuid
import sys

# --- Firebase Initialization ---
try:
    cred = credentials.Certificate('shanky-d5fa7-firebase-adminsdk-zsdrg-bfe3e8546c.json')
    # Check if the app is already initialized to prevent errors
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Successfully connected to Firestore.")
except Exception as e:
    print(f"FATAL: Failed to connect to Firestore. Please ensure your service account key is correct.")
    print(f"Error: {e}")
    sys.exit(1)

def add_session(msgs, escalation=False):
    """
    Adds a new session document to the 'sessions' collection in Firestore.
    """
    if not db:
        print("Firestore is not connected. Cannot add session.")
        return None

    sid = str(uuid.uuid4())
    sessions_collection = db.collection('sessions')
    session_doc = sessions_collection.document(sid)

    data = {
        'sid': sid,
        's_updateTime': datetime.datetime.now(datetime.timezone.utc),
        's_msgs_list': msgs,
        's_escalation': escalation
    }

    try:
        session_doc.set(data)
        print(f"Successfully added session with ID: {sid}")
        return sid
    except Exception as e:
        print(f"Error adding session: {e}")
        return None

def add_message_to_session(sid, new_message, escalation=False):
    """
    Appends a new message to an existing session's message list.
    """
    if not db or not sid:
        print("Firestore is not connected or Session ID is missing.")
        return
    
    session_doc_ref = db.collection('sessions').document(sid)

    try:
        session_doc_ref.update({
            's_msgs_list': firestore.ArrayUnion([new_message]),
            's_updateTime': datetime.datetime.now(datetime.timezone.utc),
            's_escalation': escalation
        })
        print(f"Successfully appended message to session {sid}.")
    except Exception as e:
        print(f"Error updating session {sid}: {e}. The session may not exist.")


def get_all_sessions():
    """
    Retrieves and prints all documents from the 'sessions' collection.
    """
    if not db:
        print("Firestore is not connected. Cannot get sessions.")
        return []

    try:
        docs = db.collection('sessions').stream()
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        print(f"Error getting sessions: {e}")
        return []

def get_session_by_id(sid):
    """
    Retrieves a single session document by its ID.
    """
    if not db or not sid:
        return None
    
    try:
        doc = db.collection('sessions').document(sid).get()
        return doc.to_dict() if doc.exists else None
    except Exception as e:
        print(f"Error retrieving session {sid}: {e}")
        return None

# #### NEW FUNCTION TO ADD AT THE END OF THE FILE ####
def get_recent_messages(sid, last_n=4):
    """
    Retrieves the last N messages from a given session for context.

    Args:
        sid (str): The ID of the session.
        last_n (int): The number of recent messages to retrieve.

    Returns:
        list: A list of the last N message dictionaries, or an empty list.
    """
    if not db or not sid:
        return []

    session_data = get_session_by_id(sid)
    if session_data and 's_msgs_list' in session_data:
        # Return the last 'last_n' messages from the list
        return session_data['s_msgs_list'][-last_n:]
    return []