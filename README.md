# 🤖 MekaBase: Your AI-Powered Mekanism Expert

[![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![Powered by Google Gemini](https://img.shields.io/badge/Powered%20by-Google%20Gemini-4285F4)](https://ai.google.dev/)
[![Vector DB: Chroma](https://img.shields.io/badge/Vector%20DB-Chroma-E75480)](https://www.trychroma.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Ever found yourself drowning in Mekanism wiki tabs, trying to figure out the optimal setup for a Fusion Reactor or the recipe for a Polonium Pellet? **MekaBase** is here to help.

This project is a Retrieval-Augmented Generation (RAG) agent that acts as your personal expert on the **Mekanism** Minecraft mod. Ask it a question in plain English, and it will search its knowledge base—scraped directly from the official Mekanism wiki—to give you a detailed, context-aware answer.

## ✨ Features

- **Conversational AI:** Ask complex questions and get answers, just like talking to a human expert.
- **Up-to-Date Knowledge:** The knowledge base is built by scraping the [Mekanism Wiki](https://wiki.aidancbrady.com), ensuring the information is current.
- **Intelligent Scraping:** Uses the Gemini 1.5 model to intelligently parse and chunk scraped web content, preserving context and structure.
- **Semantic Search:** Leverages ChromaDB and Gemini embeddings to understand the *meaning* of your query, not just keywords.
- **Extensible:** Easily add new data sources or fine-tune the agent's behavior.

## 🚀 Demo

Here's a quick look at what interacting with MekaBase is like:

```sh
$ python agent.py
Enter your query (or type 'exit' to quit):
> How do I start a Fusion Reactor?

To start a Fusion Reactor, you need to achieve a plasma temperature of 100 million Kelvin (100MK) and have a filled Hohlraum in the reactor's inventory.

There are two primary methods to reach this temperature:

1.  **Laser Ignition:** Fire a laser with at least 1 Giga-Forge-Energy (GFE) at the Laser Focus Matrix. You can use Laser Amplifiers to accumulate and control the laser's energy release with a redstone signal. This method instantly starts the reactor if a Hohlraum is present.

2.  **Resistive Heating:** Gradually heat the reactor by connecting a heat source, like a Resistive Heater, to a Fusion Reactor Port. This method requires a significant amount of energy (around 18 GFE total) but can be faster if you don't have a powerful laser setup.

Remember, the reactor will not start on its own and will begin consuming fuel as soon as the reaction is initiated.
```

## ⚙️ How It Works

MekaBase operates in two main phases: Data Ingestion and Query Processing.



1.  **Web Scraper (`scraper.py`):**
    - The script systematically crawls the [Mekanism Wiki's "All Pages"](https://wiki.aidancbrady.com/wiki/Special:AllPages) section.
    - It scrapes the raw HTML content from each page.

2.  **AI-Powered Chunking (`scraper_tools.py`):**
    - The raw HTML and section titles are passed to the **Google Gemini Pro** model.
    - Gemini intelligently segments the content into logical, structured JSON chunks (e.g., separating "Usage" from "Crafting"). This is far more robust than simple text splitting.

3.  **Vectorization & Storage (`agent.py` & `scraper_tools.py`):**
    - The structured text chunks are flattened and processed.
    - Each chunk is passed to a **Gemini Embedding Model**, which converts the text into a numerical vector (an embedding).
    - These embeddings, along with the original text and metadata, are stored in a local **ChromaDB** vector database.

4.  **The RAG Agent (`agent.py`):**
    - When you enter a query:
        a. Your question is also converted into an embedding using the same model.
        b. ChromaDB performs a similarity search, retrieving the top N text chunks from the database that are most semantically related to your query.
        c. Your original query and the retrieved "relevant snippets" are combined into a new prompt.
        d. This combined prompt is sent to **Gemini Pro**, which synthesizes the information into a coherent, human-readable answer.

## 🛠️ Tech Stack

- **Language:** Python
- **LLM & Embeddings:** Google Gemini API
- **Vector Database:** ChromaDB
- **Web Scraping:** BeautifulSoup, Requests
- **Data Handling:** Pandas

## 🔧 Setup & Usage

Follow these steps to get your own MekaBase agent running locally.

### 1. Prerequisites

- Python 3.9 or higher
- A Google AI Studio API Key. You can get one for free [here](https://aistudio.google.com/app/apikey).

### 2. Installation

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/acroticguy/MekaBase.git
    cd MekaBase
    ```

2.  **Create a virtual environment (recommended):**
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the dependencies:**
    ```sh
    pip install -r requirements.txt
    ```
    *(Note: A `requirements.txt` file is not in the repo, but based on the imports, you'll need: `pip install google-generativeai chromadb python-dotenv pandas beautifulsoup4 requests pydantic`)*

### 3. Configuration

1.  Create a file named `.env` in the root of the project.
2.  Add your Google API key to it. It should look like this:

    ```env
    # .env
    GOOGLE_API_KEY="YOUR_API_KEY_HERE"
    GEMINI_MODEL="models/gemini-1.5-flash"
    GEMINI_EMBEDDING_MODEL="models/embedding-001"
    SYS_INSTRUCTION_SCRAPER="You are an expert at parsing HTML content from a MediaWiki page..." # Or your preferred instruction
    ```

### 4. Running the Agent

The process is a two-step: first, you populate the database, then you run the agent to chat with it.

1.  **Populate the Database:**
    - Run the scraper to fetch all the latest data from the wiki. This will create/update `scraped_wiki_data.json`.
      ```sh
      python scraper.py
      ```
    - Next, open `agent.py`, and **uncomment** the line to populate the database:
      ```python
      # agent.py
      agent = Agent()
      agent.populate_db('scraped_wiki_data.json')  # <-- UNCOMMENT THIS LINE
      while True:
          # ...
      ```
    - Run the script. It will take some time as it embeds and adds each chunk to ChromaDB.
      ```sh
      python agent.py
      ```
    - Once it finishes and says "Database populated", you can stop the script (`Ctrl+C`).

2.  **Run the Chat Agent:**
    - **Re-comment** the `populate_db` line in `agent.py` to prevent it from running every time.
      ```python
      # agent.py
      agent = Agent()
      # agent.populate_db('scraped_wiki_data.json')  # <-- COMMENT THIS LINE AGAIN
      while True:
          # ...
      ```
    - Now, run the agent to start chatting!
      ```sh
      python agent.py
      ```

## 📂 Project Structure

```
├── .gitignore
├── README.md
├── agent.py            # The main RAG agent and chat loop.
├── chroma_db/          # Local storage for the Chroma vector database.
├── scraper.py          # Scrapes the Mekanism wiki.
├── scraper_tools.py    # Helper classes for Gemini API and ChromaDB.
├── scraped_wiki_data.json # Raw structured data from the scraper.
└── scraped_wiki_data.csv  # CSV version of the scraped data.
```

## 💡 Future Improvements

- [ ] **Web Interface:** Build a simple UI using Streamlit or Gradio.
- [ ] **Containerization:** Add a `Dockerfile` for easy deployment.
- [ ] **Incremental Scraping:** Only scrape pages that have been updated since the last run.
- [ ] **Advanced RAG:** Implement more sophisticated RAG techniques like query rewriting or reranking.

## 🙏 Acknowledgements

- The entire **Mekanism Dev Team** for creating such an incredible mod.
- The community contributors to the **[Official Mekanism Wiki](https://wiki.aidancbrady.com)** for documenting it all.
```
