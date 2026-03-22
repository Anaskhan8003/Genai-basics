from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

load_dotenv()

# Load PDF
loader = PyPDFLoader("/home/anas/genai-basics/rag/attention_u_need.pdf")
documents = loader.load()

# Split into chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(documents)
print(f"Total chunks: {len(chunks)}")

# Embed and store
embedding_model = HuggingFaceEmbeddings(model="sentence-transformers/all-MiniLM-L6-v2")
vector_store = Chroma(
    collection_name="learn_rag",
    embedding_function=embedding_model,
    host="localhost",
    port=8000,
)

vector_store.add_documents(chunks)
print("Ingestion complete!")
