from typing_extensions import TypedDict
from typing import Annotated
from dotenv import load_dotenv
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.mongodb import MongoDBSaver

load_dotenv()

llm = init_chat_model(
    model="gemini-3.1-flash-lite-preview",
    model_provider="google-genai"
)

class State(TypedDict):
    messages: Annotated[list, add_messages]

def chatbot(state: State):
    response = llm.invoke(state.get("messages"))
    return { "messages": [response]}

graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()

def compile_graph_with_checkpointer(checkpointer):
    return graph_builder.compile(checkpointer=checkpointer)
    
DB_URL = "mongodb://admin:admin@localhost:27017"
with MongoDBSaver.from_conn_string(DB_URL) as checkpointer:
    graph_with_checkpointer = compile_graph_with_checkpointer(checkpointer=checkpointer)

    config = {
        "configurable": {
            "thread_id": "anas"
            }
        }
    
    for chunk in graph_with_checkpointer.stream(
        State({"messages": ["I am John"]}),
        config,
        stream_mode="values"
    ):
        chunk["messages"][-1].pretty_print()



# (START) -> chatbot -> (END)

# state = { message: ["Hey there"] }
# node runs: chatbot(state: ["Hey There"]) -> ["Hi, This is a message from Chatbot Node"]

# Checkpointer (anas) = Hey, My Name is anas khan