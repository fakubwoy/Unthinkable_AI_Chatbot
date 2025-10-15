import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import datetime
import uuid

# --- Firebase Initialization ---
# Important: Replace 'path/to/your/serviceAccountKey.json' with the actual path to your Firebase service account key.
# You can download this file from your Firebase project settings.
try:
    cred = credentials.Certificate('shanky-d5fa7-firebase-adminsdk-zsdrg-bfe3e8546c.json')
    db = firestore.client()
    print("Successfully connected to Firestore.")
except Exception as e:
    print(f"Failed to connect to Firestore. Please ensure your service account key is correct.")
    print(f"Error: {e}")
    db = None

def add_session(msgs, escalation=False):
    """
    Adds a new session document to the 'sessions' collection in Firestore.
    A unique session ID is generated automatically using UUID.

    Args:
        msgs (list): A list of messages in the session.
        escalation (bool): A boolean indicating if the session is escalated.
    
    Returns:
        str: The generated session ID, or None if the operation fails.
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
    Appends a new message to an existing session's message list and updates the timestamp and escalation status.

    Args:
        sid (str): The ID of the session to update.
        new_message (str): The new message to append.
        escalation (bool, optional): The new escalation status. Defaults to False.
    """
    if not db:
        print("Firestore is not connected. Cannot add message.")
        return

    if not sid:
        print("Session ID is required to add a message.")
        return
    
    session_doc_ref = db.collection('sessions').document(sid)

    try:
        # Atomically add a new message and update the escalation status.
        # This also updates the last update time for the session.
        session_doc_ref.update({
            's_msgs_list': firestore.ArrayUnion([new_message]),
            's_updateTime': datetime.datetime.now(datetime.timezone.utc),
            's_escalation': escalation
        })
        print(f"Successfully appended message to session {sid}. Escalation set to: {escalation}")
    except Exception as e:
        print(f"Error updating session {sid}: {e}. The session may not exist.")


def get_all_sessions():
    """
    Retrieves and prints all documents from the 'sessions' collection.
    """
    if not db:
        print("Firestore is not connected. Cannot get sessions.")
        return []

    sessions_collection = db.collection('sessions')
    try:
        docs = sessions_collection.stream()
        sessions = []
        for doc in docs:
            sessions.append(doc.to_dict())
        return sessions
    except Exception as e:
        print(f"Error getting sessions: {e}")
        return []

def get_session_by_id(sid):
    if not db:
        print("Firestore is not connected. Cannot get session.")
        return None

    if not sid:
        print("Session ID is required to get a session.")
        return None
    
    session_doc_ref = db.collection('sessions').document(sid)

    try:
        doc = session_doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        else:
            print(f"No session found with ID: {sid}")
            return None
    except Exception as e:
        print(f"Error retrieving session {sid}: {e}")
        return None