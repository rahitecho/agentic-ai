import os
from dotenv import load_dotenv
from phi.knowledge.pdf import PDFUrlKnowledgeBase
from phi.vectordb.pgvector.pgvector2 import PgVector2
import psycopg2

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

db_url = "postgresql+psycopg://techovarya:F00tball@localhost:5432/agentic-ai"

def debug_knowledge_base():
    # Check database connection
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="agentic-ai",
            user="techovarya",
            password="F00tball"
        )
        print("✅ Database connection successful")
        
        cur = conn.cursor()
        
        # Check if ai schema exists
        cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'ai';")
        schema_exists = cur.fetchone()
        print(f"AI schema exists: {bool(schema_exists)}")
        
        # Check if recipes table exists
        cur.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'ai' AND tablename = 'recipes';")
        table_exists = cur.fetchone()
        print(f"Recipes table exists: {bool(table_exists)}")
        
        if table_exists:
            # Check number of records
            cur.execute("SELECT COUNT(*) FROM ai.recipes;")
            count = cur.fetchone()[0]
            print(f"Number of records in ai.recipes: {count}")
            
            if count > 0:
                # Show sample records
                cur.execute("SELECT name, LEFT(content, 100) FROM ai.recipes LIMIT 3;")
                records = cur.fetchall()
                print("\nSample records:")
                for i, (name, content) in enumerate(records, 1):
                    print(f"{i}. Name: {name}")
                    print(f"   Content preview: {content}...")
                    print()
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")
    
    # Test knowledge base search
    try:
        print("\n--- Testing Knowledge Base ---")
        knowledge_base = PDFUrlKnowledgeBase(
            urls=["https://phi-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
            vector_db=PgVector2(collection="recipes", db_url=db_url)
        )
        
        # Try searching
        results = knowledge_base.search("Thai dishes")
        print(f"Search results count: {len(results)}")
        
        if results:
            print("\nFirst search result:")
            print(f"Content: {results[0].content[:200]}...")
        else:
            print("No search results found - knowledge base might be empty")
            
    except Exception as e:
        print(f"❌ Knowledge base search error: {e}")

if __name__ == "__main__":
    debug_knowledge_base()