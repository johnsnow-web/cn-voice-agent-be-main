# from langchain_community.chat_message_histories import RedisChatMessageHistory
# from langchain.memory import ConversationBufferMemory

# def get_session_memory(session_id: str):
#     """Retrieve memory for a session (Redis-backed)."""
#     message_history = RedisChatMessageHistory(
#         url="redis://localhost:6379/0",
#         session_id=session_id,
#         ttl=3600  # Expire after 1 hour
#     )
    
#     return ConversationBufferMemory(
#         memory_key="chat_history",
#         chat_memory=message_history,
#         return_messages=True
#     )