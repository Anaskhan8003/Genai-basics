from mem0 import Memory
import os
from dotenv import load_dotenv
from google import genai
import json

load_dotenv()

client = genai.Client()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

config = {
    "version": "v1.1",
    "embedder": {
        "provider": "gemini",
        "config": { "api_key": GEMINI_API_KEY, "model": "gemini-embedding-001"}
    },
    "llm": {
        "provider": "gemini",
        "config": { "api_key": GEMINI_API_KEY, "model": "gemini-2.5-flash-lite"}
    },
    "graph_store":{
        "provider": "neo4j",
        "config": {
            "url": "neo4j+s://a2214b7b.databases.neo4j.io",
            "username": "a2214b7b",
            "password": "PigF1k5XIgzuIK7DR7abcWxd0gGpSjsqe3KfjiCbXH0",
            "database": "a2214b7b"
        }
    },
    "vector_store": {
        "provider": "chroma",
        "config": {
            "host": "localhost",
            "port": 8000
        }
    }
}

mem_client = Memory.from_config(config)

while True:
    
    user_query = input("> ")

    search_memory = mem_client.search(query=user_query, user_id="anaskhan")

    memory_about_user = search_memory

    memories = [
        f"ID: {mem.get("id")}\nMemory: {mem.get("memory")}" 
        for mem in search_memory.get("results")
    ]

    print("Found Memories", memories)

    SYSTEM_PROMPT = f"""
        Here is th context about the user:
        {json.dumps(memories)}
"""

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-preview",
        contents=[user_query, SYSTEM_PROMPT]
    )

    ai_response = response.text

    print("AI:", ai_response)

    mem_client.add(
        user_id="anaskhan",
        messages=[
            { "role": "user", "content": user_query},
            { "role": "assistant", "content": ai_response }
        ]
    )

    print("Memory has been saved...")