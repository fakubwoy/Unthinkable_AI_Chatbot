import chromadb

def query_collection(collection, user_query, n_results=5):
    results = collection.query(
        query_texts=[user_query],
        n_results=n_results
    )
    return results['documents']