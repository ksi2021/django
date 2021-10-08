import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.utils import dateformat

from .models import Order


class OrderWS(WebsocketConsumer):
    def user(self, order):
        try:
            return order.customer.user.username
        except:
            return 'Anonymous'

    def result(self):
        order = Order.objects.all()
        result = [{
            'id': i.id,
            'customer': self.user(i),
            'products': [{
                'product': j.product.name,
                'final_price': int(j.final_price),
                'qty': j.qty,
                'is_custom': j.product.is_custom,
                'description': j.product.description
            } for j in i.cart.products.all()],
            'final_price': int(i.cart.final_price),
            'phone': i.phone,
            'address': i.address,
            'entrance': i.entrance,
            'floor_number': i.floor_number,
            'apartment_number': i.apartment_number,
            'status': i.status,
            'comment': i.comment,
            'type_delivery': i.buying_type,
            'created_at': dateformat.format(i.created_at.astimezone(), 'd E Y, H:i'),
            'updated_at': dateformat.format(i.updated_at.astimezone(), 'd E Y, H:i'),
            # 'created_at': i.created_at,
            # 'updated_at': i.updated_at,
        } for i in order]
        return result

    def connect(self):
        self.room_group_name = 'chat'

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': self.result()
            }
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': self.result()
            }
        )

    def chat_message(self, event):
        self.send(text_data=json.dumps({
            'message': self.result()
        }))
