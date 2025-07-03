from scraper_tools import GeminiClient, ChromaDB, flatten_meka_data
import json
import time

class Agent:
    def __init__(self):
        self.chat = GeminiClient().create_agent_chat()
        self.db = ChromaDB("meka_db")

    def process_query(self, query):
        res = self.db.get_relevant_passages(query)
        prompt = f"{query}\n\nRelevant snippets:\n"
        for i, passage in enumerate(res):
            prompt += f"{i + 1}. {passage}\n"
        response = self.chat.send_message(prompt)

        return response.text

    def populate_db(self, data_file):
        """
        Populate the ChromaDB with the provided data.
        """
        with open(data_file, 'r') as file:
            data = json.load(file)

        data = flatten_meka_data(data)

        for i, chunk in enumerate(data):
            if chunk and 'text' in chunk and chunk['text'].strip():
                self.db.add_chunk(chunk, i)
                time.sleep(1)
        print(f"Database populated with {len(data)} chunks.")

agent = Agent()
# agent.populate_db('scraped_wiki_data.json')  # Populate the database with scraped data
while True:
    print("Enter your query (or type 'exit' to quit):")
    res = input()
    if res.lower() == 'exit':
        break
    testing = agent.process_query(res)  # Example query
    print(testing)  # Print the response from the agent