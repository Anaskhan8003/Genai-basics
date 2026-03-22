from dotenv import load_dotenv
from typing_extensions import TypedDict
from typing import Optional, Literal
from langgraph.graph import StateGraph, START, END
from google import genai

load_dotenv()

client = genai.Client()

class State(TypedDict):
    user_query: str
    llm_output: Optional[str]
    is_good: Optional[bool]

def chatbot(state: State):
    print("Chatbot Node", state)
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-preview",
        contents=state.get("user_query")
    )
    state["llm_output"] = response.text
    return state

def evaluate_response(state: State) -> Literal["chatbot_openai", "endnode"]:
    print("evaluate_response Node", state)
    if False:
        return "endnode"
    
    return "chatbot_openai"

def chatbot_openai(state: State):
    print("chatbot_openai Node", state)
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=state.get("user_query")
    )
    state["llm_output"] = response.text
    return state

def endnode(state: State):
    print("endnode Node", state)
    return state

graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("chatbot_openai", chatbot_openai)
graph_builder.add_node("endnode", endnode)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", evaluate_response)

graph_builder.add_edge("chatbot_openai", "endnode")
graph_builder.add_edge("endnode", END)

graph = graph_builder.compile()

updated_state = graph.invoke(State({"user_query": "Hey, What is 2 + 2?"}))
print(updated_state)