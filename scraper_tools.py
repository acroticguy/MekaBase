from pydantic import BaseModel
import google.genai
from dotenv import load_dotenv
import os
import json

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
        load_dotenv()
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        self.model = os.environ.get("GEMINI_MODEL")
        self.system_ins = os.environ.get("SYS_INSTRUCTION_SCRAPER")
        self.client = google.genai.Client(api_key=self.api_key)

        self.scraper = self.client.chats.create(
            model=self.model,
            config={
                "response_mime_type": "application/json",
                "response_schema": list[Chunk],
                'system_instruction': self.system_ins,
            }
        )

    def generate_chunks(self, contents, titles):
        """
        Generate chunks of text using the Gemini API.

        Args:
            contents (list): A list of HTML content strings to process.

        Returns:
            list: A list of Chunk objects.
        """
        msg = f"Those are the titles: {titles}. Now, please extract the corresponding paragraphs from the following contents.\n\n {contents}"

        response = self.scraper.send_message(msg)

        res = json.loads(response.text)

        return res

    def get_client(self):
        # Singleton pattern to return a single GeminiClient instance
        if not hasattr(self, '_instance'):
            self._instance = GeminiClient()
        return self._instance