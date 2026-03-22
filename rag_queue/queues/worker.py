from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import chromadb
from google import genai


load_dotenv()

client = genai.Client()

# Vector Embeddings
embedding_model = HuggingFaceEmbeddings(
    model="sentence-transformers/all-MiniLM-L6-v2"
)

vector_store = Chroma(
    collection_name="learn_rag",
    embedding_function=embedding_model,
    host="localhost",
    port=8000,
)


async def process_query(query:str):
    print("Searching Chunks", query)
    search_results = vector_store.similarity_search(query=query)

    context = "\n\n\n".join([f"Page Content: {result.page_content}\nPage Number: {result.metadata['page_label']}\nFile Location: {result.metadata['source']}" for result in search_results])

    SYSTEM_PROMPT = f"""
    You are a helpfull AI Assistant who answeres user query based on the available context retrieved from a PDF file along with page_contents and page number.

    You should only ans the user based on the following context and navigate the user to open the right page number to know more.

    Context:
    {context}
    """

    response = client.models.generate_content(
    model="gemini-3.1-flash-lite-preview",
    contents=query,
    config={
        "system_instruction": SYSTEM_PROMPT,
    }
)


    print(f"Response: {response.text}")
    return response.text

