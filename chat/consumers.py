import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Message, Notification

User = get_user_model()

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
        else:
            self.group_name = f"notify_{self.user.id}"
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def notify(self, event):
        await self.send(text_data=json.dumps(event['payload']))

class CallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
        else:
            self.room_group_name = f'call_{self.user.id}'
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        target_id = data.get('target_id')
        payload = data.get('payload')

        if target_id:
            target_group = f'call_{target_id}'
            await self.channel_layer.group_send(
                target_group,
                {
                    'type': 'signaling_message',
                    'action': action,
                    'caller_id': self.user.id,
                    'payload': payload
                }
            )

    async def signaling_message(self, event):
        action = event['action']
        caller_id = event['caller_id']
        payload = event['payload']

        await self.send(text_data=json.dumps({
            'action': action,
            'caller_id': caller_id,
            'payload': payload
        }))

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
        else:
            self.other_user_id = self.scope['url_route']['kwargs']['user_id']
            # Create a unique room name for the two users
            ids = sorted([int(self.user.id), int(self.other_user_id)])
            self.room_group_name = f'chat_{ids[0]}_{ids[1]}'
            
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message')
        voice_url = data.get('voice_url')
        
        other_user = await self.get_other_user()
        
        if message:
            await self.save_message(other_user, message)
            
            # Create Persistent Notification in Database
            await self.create_persistent_notification(other_user, f"New message from {self.user.username}")
            
            # Trigger real-time notification to the empty toast
            await self.channel_layer.group_send(
                f"notify_{other_user.id}",
                {
                    "type": "notify",
                    "payload": {
                        "message": f"New message from {self.user.username}",
                        "link": f"/chat/{self.user.id}/",
                        "type": "message"
                    }
                }
            )
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'voice_url': voice_url,
                'sender_id': self.user.id,
                'sender_name': self.user.username,
                'sender_pic': self.user.avatar_url
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'voice_url': event['voice_url'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'sender_pic': event.get('sender_pic')
        }))

    @database_sync_to_async
    def create_persistent_notification(self, receiver, message):
        return Notification.objects.create(
            recipient=receiver,
            actor=self.user,
            message=message,
            link=f"/chat/{self.user.id}/"
        )

    @database_sync_to_async
    def get_other_user(self):
        return User.objects.get(id=self.other_user_id)

    @database_sync_to_async
    def save_message(self, receiver, content):
        return Message.objects.create(
            sender=self.user,
            receiver=receiver,
            text_content=content
        )
