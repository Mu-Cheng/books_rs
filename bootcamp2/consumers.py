# consumers.py

# -*- coding: utf-8 -*-

from channels.generic.websocket import AsyncWebsocketConsumer

import time
# from asgiref.sync import async_to_sync


# 自定义websocket处理类
class RecommendStatus(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add("rs_loging", self.channel_name)

    async def chat_message(self, event):
        await self.send(text_data=event["text"])



    async def receive(self, text_data=None, bytes_data=None):
        # 收到信息时调用

        # 信息单发
        # await self.send(text_data="Hello world!")

        # 信息群发

        # await self.send(text_data=text_data+"1234")
        # await self.send(text_data="fdfasdf")

        # time.sleep(10)
        # print('123')
        # self.send(text_data="123")
        #
        # for i in range(1000):
        #     print('1234')
        #     await self.send(text_data="fdfasdf")
        #     time.sleep(5)
        await self.channel_layer.group_send(
            "rs_loging",
            {
                "type": "chat.message",
                "text": "Hello world!",
            },
        )


    async def disconnect(self, close_code):
        # 连接关闭时调用
        # 将关闭的连接从群组中移除
        await self.channel_layer.group_discard("rs_loging", self.channel_name)

        await self.close()
