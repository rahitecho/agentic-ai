import typer
from typing import Optional, List
from phi.assistant import Assistant
from phi.storage.assistant.postgres import PgAssistantStorage
from phi.knowledge.pdf import PDFUrlKnowledgeBase
from phi.vectordb.pgvector.pgvector2 import PgVector2

import os
from dotenv import load_dotenv
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
db_url = "postgresql+psycopg://techovarya:F00tball@localhost:5432/agentic-ai"

knowledge_base = PDFUrlKnowledgeBase(
    urls=["https://phi-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
    vector_db=PgVector2(collection="recipes", db_url=db_url)
)

storage = PgAssistantStorage(table_name="pdf_assistant", db_url=db_url)

app = typer.Typer()

@app.command("chat")
def pdf_assistant(new: bool = False, user: str = "user", load_knowledge: bool = False):
    run_id: Optional[str] = None

    # Check if knowledge base exists, if not, load it automatically
    try:
        vector_db = PgVector2(collection="recipes", db_url=db_url)
        vector_db.search(query="test", limit=1)
    except Exception:
        print("Knowledge base not found. Loading PDF...")
        try:
            knowledge_base.load(recreate=True)
            print("✅ Knowledge base loaded successfully!")
        except Exception as e:
            print(f"❌ Error loading knowledge base: {e}")
            return

    # Load knowledge base if explicitly requested
    if load_knowledge:
        print("Reloading knowledge base...")
        try:
            knowledge_base.load(recreate=True)
            print("✅ Knowledge base reloaded successfully!")
        except Exception as e:
            print(f"❌ Error loading knowledge base: {e}")
            return

    # Handle run_id logic - key fix here
    if not new:
        try:
            existing_run_ids: List[str] = storage.get_all_run_ids(user)
            if existing_run_ids:
                # Use the most recent run_id (last in list)
                run_id = existing_run_ids[-1]
                print(f"Found existing run_id: {run_id}")
            else:
                print("No existing runs found, creating new one")
        except Exception as e:
            print(f"Error getting run IDs: {e}")
            print("Creating new run due to error")

    # Create assistant with proper configuration
    assistant = Assistant(
        run_id=run_id,
        user_id=user,
        knowledge_base=knowledge_base,
        storage=storage,
        show_tool_calls=True,
        search_knowledge=True,
        read_chat_history=True,
        # Add these parameters for better memory handling
        add_chat_history_to_messages=True,
        num_history_messages=20,  # Adjust based on your needs
    )
    
    # Print run information
    if run_id is None:
        print(f"Started New Run: {assistant.run_id}\n")
    else:
        print(f"Continuing Run: {run_id}\n")
        # Verify chat history is loaded
        try:
            chat_history = storage.read_chat_history(run_id)
            print(f"Loaded {len(chat_history) if chat_history else 0} previous messages\n")
        except Exception as e:
            print(f"Warning: Could not load chat history: {e}\n")

    assistant.cli_app(markdown=True)

@app.command("list")
def list_runs(user: str = "user"):
    """List all existing runs for debugging"""
    try:
        run_ids = storage.get_all_run_ids(user)
        print(f"Existing runs for user '{user}':")
        for i, run_id in enumerate(run_ids):
            print(f"  {i+1}. {run_id}")
            try:
                history = storage.read_chat_history(run_id)
                msg_count = len(history) if history else 0
                print(f"     Messages: {msg_count}")
            except:
                print("     Messages: Unknown")
    except Exception as e:
        print(f"Error listing runs: {e}")

@app.command("clear")
def clear_runs(user: str = "user"):
    """Clear all runs for a user"""
    try:
        run_ids = storage.get_all_run_ids(user)
        for run_id in run_ids:
            storage.delete_run(run_id)
        print(f"Cleared {len(run_ids)} runs for user '{user}'")
    except Exception as e:
        print(f"Error clearing runs: {e}")

if __name__ == "__main__":
    app()