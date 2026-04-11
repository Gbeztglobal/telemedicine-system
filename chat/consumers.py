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
        action = data.get('action', 'send_message')
        message_id = data.get('message_id')
        message_text = data.get('message')
        voice_url = data.get('voice_url')
        parent_id = data.get('parent_id')
        
        other_user = await self.get_other_user()
        
        if action == 'send_message' and (message_text or voice_url):
            new_msg = await self.save_message(other_user, message_text, voice_url, parent_id)
            
            # Quoted Context for Broadcast (if reply)
            parent_text = await self.get_parent_text(parent_id) if parent_id else None
            
            # Notification only for new messages
            await self.create_persistent_notification(other_user, f"New message from {self.user.username}")
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'action': 'new',
                    'message_id': new_msg.id,
                    'message': message_text,
                    'voice_url': voice_url,
                    'parent_id': parent_id,
                    'parent_text': parent_text,
                    'sender_id': self.user.id,
                    'sender_name': self.user.username,
                    'sender_pic': self.user.avatar_url,
                    'timestamp': new_msg.timestamp.strftime('%H:%M')
                }
            )

        elif action == 'edit_message' and message_id and message_text:
            success = await self.update_message(message_id, message_text)
            if success:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'action': 'edit',
                        'message_id': message_id,
                        'message': message_text
                    }
                )

        elif action == 'delete_message' and message_id:
            success = await self.delete_message(message_id)
            if success:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'action': 'delete',
                        'message_id': message_id
                    }
                )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def get_parent_text(self, parent_id):
        try:
            return Message.objects.get(id=parent_id).text_content
        except:
            return None

    @database_sync_to_async
    def create_persistent_notification(self, receiver, message):
        return Notification.objects.create(
            recipient=receiver,
            actor=self.user,
            message=message,
            link=f"/chat/room/{self.user.id}/"
        )

    @database_sync_to_async
    def get_other_user(self):
        return User.objects.get(id=self.other_user_id)

    @database_sync_to_async
    def save_message(self, receiver, content, voice_url=None, parent_id=None):
        parent = Message.objects.get(id=parent_id) if parent_id else None
        return Message.objects.create(
            sender=self.user,
            receiver=receiver,
            text_content=content,
            voice_note=voice_url, # Note: this assumes url is already stored if coming from another source, but usually voice is a file field.
            parent_message=parent
        )

    @database_sync_to_async
    def update_message(self, message_id, new_content):
        from django.utils import timezone
        try:
            msg = Message.objects.get(id=message_id, sender=self.user)
            # 50 second check
            if (timezone.now() - msg.timestamp).total_seconds() <= 50:
                msg.text_content = new_content
                msg.is_edited = True
                msg.save()
                return True
        except Message.DoesNotExist:
            pass
        return False

    @database_sync_to_async
    def delete_message(self, message_id):
        try:
            msg = Message.objects.get(id=message_id, sender=self.user)
            msg.is_deleted = True
            msg.text_content = "This message was deleted"
            msg.save()
            return True
        except Message.DoesNotExist:
            pass
        return False
