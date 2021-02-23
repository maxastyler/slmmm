import asyncio
import grpc
from grpc import aio

import slm_pb2
import slm_pb2_grpc

import time
import numpy as np


async def run() -> None:
    while True:
        async with grpc.aio.insecure_channel("localhost:50051") as channel:
            stub = slm_pb2_grpc.SLMStub(channel)
            w, h = (512, 400)
            response = await stub.SetPhaseMask(slm_pb2.PhaseMask(phasemask=np.exp(2j*np.pi*np.random.random((w, h))).tobytes(), width=w, height=h))
        print(f"Received: {response.completed}")
        time.sleep(1)

if __name__ == '__main__':
    asyncio.run(run())
