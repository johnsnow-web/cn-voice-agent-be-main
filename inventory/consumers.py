import json
from urllib.parse import parse_qs
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.exceptions import ObjectDoesNotExist
from inventory.models import User
from inventory.agent import create_agent_executor, process_message  
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            # Parse query parameters
            query_params = parse_qs(self.scope["query_string"].decode())
            user_id = query_params.get("userId", [None])[0]
            
            if not user_id:
                await self.close(code=4003)
                return

            # Get user and validate
            self.user = await self.get_user(user_id)
            if not self.user:
                await self.close(code=4001)
                return

            # Store user_id for this connection
            self.user_id = str(user_id)
            
            # Initialize agent executor and chat history
            try:
                self.agent_executor, self.chat_history = create_agent_executor(self.user_id)
            except Exception as e:
                print(f"Failed to create agent executor: {str(e)}")
                await self.close(code=4002)
                return
            
            await self.accept()
            await self.send(text_data=json.dumps({
                "status": "connected",
                "message": "WebSocket connection established",
                "user_id": self.user_id
            }))
            
        except Exception as e:
            print(f"Connection error: {str(e)}")
            await self.close(code=4000)

    @sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except (ObjectDoesNotExist, ValueError):
            return None

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data.get('message', '').strip()
            
            if not message:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'content': "Please provide a message",
                    'streaming': False
                }))
                return
            
            # Check if agent executor is initialized
            if not hasattr(self, 'agent_executor') or not self.agent_executor:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'content': "Agent not initialized. Please reconnect.",
                    'streaming': False
                }))
                return
            
            # Process the message
            response = await process_message(
                self.agent_executor,
                self.chat_history,
                {
                    "message": message,
                    "user_id": self.user_id
                }
            )
            
            await self.send(text_data=json.dumps({
                'type': 'response',
                'content': response,
                'streaming': False
            }))
            
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'content': "Invalid JSON format",
                'streaming': False
            }))
        except Exception as e:
            print(f"Error in WebSocket receive: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'content': "Sorry, I encountered an error processing your request",
                'streaming': False
            }))

    async def disconnect(self, close_code):
        print(f"WebSocket disconnected with code: {close_code}")
        # Clean up resources if needed
        if hasattr(self, 'agent_executor'):
            self.agent_executor = None
        if hasattr(self, 'chat_history'):
            self.chat_history = None