from pydantic import BaseModel
import google.genai
from dotenv import load_dotenv
import os
import json
from google.genai import types
import chromadb
from chromadb import EmbeddingFunction, Documents, Embeddings

load_dotenv()
GOOGLE_API = os.environ.get("GOOGLE_API_KEY")
EMBEDDING_MODEL = os.environ.get("GEMINI_EMBEDDING_MODEL")
client = google.genai.Client(api_key=GOOGLE_API)
db_path = "./chroma_db"

class Chunk(BaseModel):
    """
    A class to represent a chunk of text scraped from a webpage.
    """
    title: str
    text: str

    def to_dict(self):
        return {
            "title": self.title,
            "text": self.text,
        }

    def __str__(self):
        return f"Title: {self.title}, Text Length: {len(self.text)}"
    
class GeminiClient:
    """
    A class to interact with the Gemini API for text processing.
    """
    def __init__(self):
        self.model = os.environ.get("GEMINI_MODEL")
        self.system_ins = os.environ.get("SYS_INSTRUCTION_SCRAPER")
        self.client = client

        print("GeminiClient initialized with model:", self.model)


    def generate_chunks(self, contents, titles):
        """
        Generate chunks of text using the Gemini API.

        Args:
            contents (list): A list of HTML content strings to process.

        Returns:
            list: A list of Chunk objects.
        """
        msg = f"Those are the titles: {titles}. Now, please extract the corresponding paragraphs from the following contents.\n\n {contents}"
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=msg,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": list[Chunk],
                    'system_instruction': self.system_ins,
                }
            )
        except Exception as e:
            print(f"Error generating content: {e}")
            return [
                {'title': 'Error', 'text': ''}
            ]

        res = json.loads(response.text.strip())

        return res
    
    def create_agent_chat(self):
        """
        Create a chat session with the Gemini API.

        Args:
            instructions (str): Instructions for the chat session.

        Returns:
            google.genai.types.ChatSession: The created chat session.
        """

        instructions = f"""You are an expert in the Minecraft Mod Mekanism. The user will ask you questions about the mod, 
        and you will provide detailed answers based on your own knowledge and the few provided snippets provided below.
        Not all snippets provide valuable information, so you should only use the snippets that are relevant to the question asked."""

        return self.client.chats.create(
            model=self.model,
            config={
                "system_instruction": instructions,
            }
        )

class GeminiEmbeddingFunction(EmbeddingFunction):
  def __call__(self, input: Documents) -> Embeddings:
    title = "Custom query"
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=input,
        config=types.EmbedContentConfig(
            task_type="retrieval_document",
            title=title
        )
    )

    return response.embeddings[0].values
    
class ChromaDB:

    def __init__(self, collection_name):
        """
        Initialize the ChromaDB client.

        Args:
            collection_name (str): The name of the collection to use.
        """
        self.client = chromadb.PersistentClient(path=db_path)
        print(self.client.list_collections())
        for collection in self.client.list_collections():
            if collection.name == collection_name:
                print(f"Found existing collection: {collection_name}")
                self.collection = self.client.get_collection(
                    name=collection_name,
                    embedding_function=GeminiEmbeddingFunction()
                    )
                return
        self.collection = self.client.create_collection(
            name=collection_name,
            embedding_function=GeminiEmbeddingFunction()
            )
        print(f"ChromaDB initialized with collection: {collection_name}")

    def add_chunk(self, chunk, id):
        """
        Add a chunk to the ChromaDB collection.

        Args:
            chunk (dict): The chunk to add.
        """
        try:
            self.collection.add(
                documents=[chunk_to_str(chunk)],
                metadatas=[{"title": chunk['title'], "page": chunk['page']}],
                ids=[str(id)],
            )
            print(f"Chunk added: {chunk['title']} ({chunk['page']})")
        except Exception as e:
            print(f"Error adding chunk to ChromaDB: {e}")

    def get_relevant_passages(self, query):
        passages = self.collection.query(query_texts=[query], n_results=10)['documents'][0]
        return passages

def flatten_meka_data(data):
    """
    Flatten the Meka data structure into a list of dictionaries.

    Args:
        data (list): The Meka data to flatten.

    Returns:
        list: A flattened list of dictionaries.
    """
    flat_data = []
    for category in data:
        for chunk in category.get('chunks', []):
            if chunk and 'text' in chunk and chunk['text'].strip():
                flat_data.append({
                    'title': chunk['title'],
                    'text': chunk['text'],
                    'page': category.get('section', ''),
                })
    return flat_data

def chunk_to_str(chunk):
    return f"{chunk['title']} ({chunk['page']}): \n{chunk['text']}"