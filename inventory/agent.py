from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain import hub
from .tools import get_tools
from typing import List, Dict, Any

def create_agent_executor(user_id: str):
    tools = get_tools(user_id)

    # Define primary and fallback LLMs
    primary_llm = ChatOpenAI(model="gpt-3.5-turbo", max_retries=2, streaming=True)
    fallback_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

    # Create fallback-enabled LLM
    llm = primary_llm.with_fallbacks([fallback_llm])

    try:
        prompt = hub.pull("hwchase17/structured-chat-agent")
    except:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an inventory management assistant. Help users manage their products, product inventory and stock levels, send all required response but in single formatted string.

Current user: {user_id}

You have access to the following tools:
{tools}


Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action:

{{
  "action": $TOOL_NAME, 
  "action_input": $INPUT
}}

Observation: the result of the action
... (this Thought/Action/Observation can repeat N times)
Thought: I now know the final answer
Action:

{{
  "action": "Final Answer",
  "action_input": "Format Response in Single Formatted String Send."
}}

Valid "action" values: "Final Answer" or {tool_names}"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

    # Initialize empty chat history
    chat_history: List[Dict[str, Any]] = []

    try:
        agent = create_structured_chat_agent(
            llm=llm,
            tools=tools,
            prompt=prompt
        )

        return AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
            return_intermediate_steps=True
        ), chat_history
    except Exception as e:
        raise ValueError(f"Failed to create agent: {str(e)}")

async def process_message(agent_executor: AgentExecutor, 
                        chat_history: List[Dict[str, Any]],
                        input_data: Dict[str, Any]):
    try:
        # Prepare input with chat history
        inputs = {
            "input": input_data.get("message", ""),
            "user_id": input_data.get("user_id", ""),
            "chat_history": [
                AIMessage(content=msg["content"]) if msg["role"] == "assistant"
                else HumanMessage(content=msg["content"])
                for msg in chat_history
            ]
        }

        response = await agent_executor.ainvoke(inputs)

        # Update chat history
        chat_history.extend([
            {"role": "user", "content": inputs["input"]},
            {"role": "assistant", "content": response["output"]}
        ])

        return response["output"]
    except Exception as e:
        print(f"Processing error: {str(e)}")
        raise