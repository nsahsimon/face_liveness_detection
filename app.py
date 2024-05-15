import asyncio
import websockets
import numpy as np
import base64
import cv2


async def process_frame(frame_data):
    # Decode base64 image
    # image_data = base64.b64decode(frame_data)
    nparr = np.frombuffer(frame_data, np.uint8)
    print(nparr[:20])
    print(f"np array shape: {nparr.shape[0]}")
    img = nparr.reshape((480, 720))
    # img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    
    if img is not None:
        print("Showing the image")
        # Display the frame
        # cv2.imshow('Frame', img)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
            # return False
    else:
        print("Image is empty")
    return True

async def echo(websocket, path):
    print("Client connected")
    try:
        async for message in websocket:
            image_bytes = message
            # await process_frame(image_bytes)
            # print(f"Received bytes length: {len(image_bytes)}")
            # print(f"Sample bytes: ${image_bytes[:20]}")
            # print(f"Received message: {message}")
            await websocket.send(f"Received image bytes of length ${len(image_bytes)}")
    except websockets.ConnectionClosed as e:
        print(f"Connection closed: {e}")
    finally:
        print("Client disconnected")

async def main():
    async with websockets.serve(echo, "0.0.0.0", 5000):
        print("WebSocket server started at ws://0.0.0.0:5000")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())



    def YUVtoRGB(byteArray):

        e = 1280*720
        Y = byteArray[0:e]
        Y = np.reshape(Y, (720,1280))

        s = e
        V = byteArray[s::2]
        V = np.repeat(V, 2, 0)
        V = np.reshape(V, (360,1280))
        V = np.repeat(V, 2, 0)

        U = byteArray[s+1::2]
        U = np.repeat(U, 2, 0)
        U = np.reshape(U, (360,1280))
        U = np.repeat(U, 2, 0)

        RGBMatrix = (np.dstack([Y,U,V])).astype(np.uint8)
        RGBMatrix = cv2.cvtColor(RGBMatrix, cv2.COLOR_YUV2RGB, 3)