import chromadb
import json

# Use a relative path for the ChromaDB data directory
client=chromadb.PersistentClient(path="./data")

collection = client.get_or_create_collection(name="FAQ")

def read_text_file(filepath):
    """
    Reads a text file and returns its content.

    Args:
        filepath (str): Path to the text file

    Returns:
        str: Content of the file, or None if error occurs
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def generate_ids_from_dict_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()

        data_list = json.loads(content)

        if not isinstance(data_list, list):
            raise ValueError("File content is not a list of dictionaries")

        num_items = len(data_list)

        id_list = [f"id{i}" for i in range(1, num_items + 1)]

        return id_list

    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found")
        return []
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in file - {e}")
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []


if __name__ == "__main__":
    # Read and parse the FAQ file using a relative path
    filepath = "./dataset/HDFC_Faq.txt"
    content = read_text_file(filepath)

    if content:
        try:
            # Parse JSON data
            faq_data = json.loads(content)

            # Extract documents (combine question and answer)
            documents = []
            metadatas = []
            ids = []

            for idx, item in enumerate(faq_data, start=1):
                # Combine question and answer for better context
                doc_text = f"Question: {item['question']}\nAnswer: {item['answer']}"
                documents.append(doc_text)

                # Add metadata
                metadatas.append({
                    "question": item['question'],
                    "answer": item['answer'],
                    "source": "HDFC_FAQ"
                })

                # Generate ID
                ids.append(f"id{idx}")

            # Add to collection
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )

            print(f"Successfully added {len(documents)} FAQ items to the collection.")

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
        except Exception as e:
            print(f"Error adding data to collection: {e}")
    else:
        print("Failed to read the file.")