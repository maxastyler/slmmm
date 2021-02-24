import asyncio
import grpc
from grpc import aio

import slm_pb2
import slm_pb2_grpc

import time
import numpy as np


async def run() -> None:
    while True:
        async with grpc.aio.insecure_channel("localhost:2002") as channel:
            stub = slm_pb2_grpc.SLMStub(channel)
            w = h = np.random.randint(10, 500)
            response = await stub.SetImage(slm_pb2.Image(image_bytes=np.random.randint(0, 255, (w, h), dtype=np.uint8).tobytes(), width=w, height=h))
        print(f"Received: {response.completed}")
        time.sleep(1)

if __name__ == '__main__':
    asyncio.run(run())
