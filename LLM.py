import chromadb
from query import query_collection
from backend import add_session, add_message_to_session, get_recent_messages
import requests
import json
import datetime

# Initialize ChromaDB client
client = chromadb.PersistentClient(path="./data")
collection = client.get_collection(name="FAQ")

# Session state (managed per request)
current_session_id = None

def rewrite_query_with_history(conversation_history, follow_up_question):
    """
    Uses the LLM to rewrite a vague follow-up question into a specific, standalone query.
    """
    history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])

    prompt = f"""Based on the following conversation history, rewrite the user's follow-up question into a complete, standalone question.

**Rules:**
- If the follow-up question is already a complete question, return it as is.
- If the follow-up is vague (e.g., "what about that?", "and for a debit card?"), expand it using the context of the last user question.
- The rewritten query should be concise and direct.

**Conversation History:**
{history_str}

**Follow-up Question:** "{follow_up_question}"

**Rewritten Standalone Question:**
"""

    url = "http://ollama:11434/api/generate"
    payload = {
        "model": "gemma:2b",
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.0}
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        rewritten_query = result.get('response', follow_up_question).strip().strip('"')
        return rewritten_query if len(rewritten_query) > 5 else follow_up_question
    except requests.exceptions.RequestException as e:
        print(f"Error rewriting query: {e}")
        return follow_up_question # Fallback to original question on error

def call_llm_for_answer(user_query, context):
    """
    Calls the Gemma model with the final prompt to get an answer.
    """
    full_prompt = f"""You are a HDFC Banking Support Assistant. Use the provided <context> to answer the user's query accurately.

Rules:
1. If the context has the answer, use it directly.
2. If the context is not relevant, say: "I don’t have this information in the FAQ. Would you like me to connect you to customer support?"
3. Never guess or hallucinate. Be professional but friendly.

<context>
{context}
</context>

User Query: {user_query}

Answer:"""

    url = "http://ollama:11434/api/generate"
    payload = {
        "model": "gemma:2b",
        "prompt": full_prompt,
        "stream": False
    }

    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        return result.get('response', 'No response generated')
    except requests.exceptions.Timeout:
        return "Error: The request to the model timed out. It may still be loading."
    except requests.exceptions.RequestException as e:
        return f"Error calling Ollama: {e}"

def answer_question(current_sid, user_query, n_results=5):
    """
    Main RAG pipeline function: Rewrite -> Retrieve -> Generate.
    """
    global current_session_id
    current_session_id = current_sid
    
    query_for_retrieval = user_query
    
    # 1. REWRITE STEP: If it's a follow-up, rewrite the query for better retrieval
    if current_session_id:
        print(f"--- Existing session ({current_session_id}) detected. Rewriting query. ---")
        history = get_recent_messages(current_session_id, last_n=4)
        if history:
            rewritten_query = rewrite_query_with_history(history, user_query)
            print(f"Original query: '{user_query}'")
            print(f"Rewritten query for retrieval: '{rewritten_query}'")
            query_for_retrieval = rewritten_query
    
    # 2. RETRIEVAL STEP: Use the (potentially rewritten) query to find context
    print(f"--- Retrieving context for: '{query_for_retrieval}' ---")
    retrieved_docs = query_collection(collection, query_for_retrieval, n_results)
    context = "\n\n".join([doc for doc_list in retrieved_docs for doc in doc_list])
    
    # 3. GENERATION STEP: Use the ORIGINAL query and retrieved context to answer
    print(f"--- Generating final answer for: '{user_query}' ---")
    answer = call_llm_for_answer(user_query, context)
    
    # 4. SESSION MANAGEMENT: Log the conversation
    user_message = {"role": "user", "content": user_query}
    assistant_message = {
        "role": "assistant",
        "content": answer,
        "context_used": context[:200] + "..." if len(context) > 200 else context,
        "retrieval_query": query_for_retrieval
    }
    
    if current_session_id is None:
        current_session_id = add_session([user_message, assistant_message])
    else:
        add_message_to_session(current_session_id, user_message)
        add_message_to_session(current_session_id, assistant_message)
    
    return {
        "answer": answer,
        "session_id": current_session_id
    }