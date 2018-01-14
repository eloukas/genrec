#!/usr/bin/env python

import asyncio
import websockets

youtube_link = 'https://www.youtube.com/watch?v=Eq3CuMDXaP'

async def send_link():
    async with websockets.connect('ws://localhost:8765') as websocket:
        await websocket.send(youtube_link)

        validation = await websocket.recv()
        print("< {}".format(validation))

asyncio.get_event_loop().run_until_complete(send_link())
