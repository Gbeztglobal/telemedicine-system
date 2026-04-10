import json
from channels.generic.websocket import AsyncWebsocketConsumer

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

    # Receive message from WebSocket
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

    # Receive message from room group
    async def signaling_message(self, event):
        action = event['action']
        caller_id = event['caller_id']
        payload = event['payload']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'action': action,
            'caller_id': caller_id,
            'payload': payload
        }))
