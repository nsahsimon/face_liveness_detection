import asyncio
import websockets
import numpy as np
import base64
import cv2
import json
import tester


handlerSelector = None
width = None
height = None
y_bytes = None
u_bytes = None
v_bytes = None
y_bpp = None
u_bpp = None
v_bpp = None

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


def YUVtoRGB():
    global handlerSelector, width, height, y_bytes, y_bpp, u_bpp, u_bytes, v_bpp, v_bytes, u_bpp, u_bytes

    Y = np.frombuffer(y_bytes, np.uint8)
    # img = y_nparr.reshape((width, height))
    # Y = np.array(y_bytes)
    Y = np.reshape(Y, (height,width))
    print(f"Y-size: ${Y.shape}")

    V = np.frombuffer(v_bytes, np.uint8)
    # V = np.repeat(V, 2, 0)
    padlength = (width//2 * height) - V.shape[0]
    print(f"v pad length: {padlength}")
    V = np.pad(V, (0, padlength), 'constant', constant_values=0)
    V = np.reshape(V, (height//2,width))
    V = np.repeat(V, 2, 0)
    print(f"V-size: ${V.shape}")

    # U = np.array(u_bytes)
    U = np.frombuffer(u_bytes, np.uint8)
    # U = np.repeat(U, 2, 0)
    padlength = (width//2 * height) - U.shape[0]
    print(f"u pad length: {padlength}")
    U = np.pad(U, (0, padlength), 'constant', constant_values=0)
    U = np.reshape(U, (height//2,width))
    U = np.repeat(U, 2, 0)
    print(f"U-size: ${U.shape}")

    RGBMatrix = (np.dstack([Y,V, U])).astype(np.uint8)
    RGBMatrix = cv2.cvtColor(RGBMatrix, cv2.COLOR_YUV2BGR, 3)

    RGBMatrix = cv2.rotate(RGBMatrix, cv2.ROTATE_90_COUNTERCLOCKWISE)
    print(f"final image size: ${RGBMatrix.shape}")
    return RGBMatrix

def YUVtoRGBO():
    global handlerSelector, width, height, y_bytes, y_bpp, u_bpp, u_bytes, v_bpp, v_bytes, u_bpp, u_bytes

    Y = np.frombuffer(y_bytes, np.uint8)
    # img = y_nparr.reshape((width, height))
    # Y = np.array(y_bytes)
    Y = np.reshape(Y, (height,width))
    print(f"Y-size: ${Y.shape}")

    # The byte you want to add
    new_byte = np.uint8(255)
    print(f"vbytes length: {len(v_bytes)}")
    V = np.frombuffer(v_bytes, np.uint8)
    V = np.pad(V, (0, 1), 'constant', constant_values=0)
    print(f"uint8length: {len(V)}")
    # print(f"v first 20: {V[:20]}")
    V = V.view(dtype=np.uint16)
    print(f"uint16length: {len(V)}")
    V = V.reshape((height//2,width//2))
    print(f"V-size: ${V.shape}")

    # The byte you want to add
    new_byte = np.uint8(255)
    print(f"vbytes length: {len(u_bytes)}")
    U = np.frombuffer(u_bytes, np.uint8)
    U = np.pad(U, (0, 1), 'constant', constant_values=0)
    print(f"uint8length: {len(U)}")
    # print(f"v first 20: {U[:20]}")
    U = U.view(dtype=np.uint16)
    print(f"uint16length: {len(U)}")
    U = U.reshape((height//2,width//2))
    print(f"U-size: ${U.shape}")

    UV = np.dstack((V, U))
    BGRMatrix = cv2.cvtColorTwoPlane(Y, V, 90)

    BGRMatrix = cv2.rotate(BGRMatrix, cv2.ROTATE_90_COUNTERCLOCKWISE)
    print(f"final image size: ${BGRMatrix.shape}")
    return BGRMatrix


async def echo(websocket, path):
    global handlerSelector, width, height, y_bytes, y_bpp, u_bpp, u_bytes, v_bpp, v_bytes, u_bpp, u_bytes
    print("Client connected")
    try:
        async for message in websocket:
            if handlerSelector == None and message == "metadata":
                handlerSelector = "metadata"
            elif handlerSelector == "metadata":
                print("Receiving metadata ....")
                decodedData = json.loads(message)
                width = decodedData['width']
                height = decodedData['height']
                y_bpp = decodedData['y_bpp']
                u_bpp = decodedData['u_bpp']
                v_bpp = decodedData['v_bpp']
                print(f"Metadata: width: {width}, height: {height}, y_bpp: {y_bpp}, u_bpp: {u_bpp}, v_bpp: {v_bpp}")
                handlerSelector = None
                await websocket.send(f"Received metadata")
            elif message == "y_bytes":
                handlerSelector = "y_bytes"
            elif handlerSelector == "y_bytes":   
                print('Getting y-plane bytes')
                y_bytes = message
                print(f"Y-plane bytes length : ${len(y_bytes)}")
                handlerSelector = None
                await websocket.send(f"Received y_bytes")
            elif message == "u_bytes":
                handlerSelector = "u_bytes"
            elif handlerSelector == "u_bytes":   
                print('Getting u-plane bytes')
                u_bytes = message
                print(f"U-plane bytes length : ${len(u_bytes)}")
                handlerSelector = None
                await websocket.send(f"Received u_bytes")
            elif message == "v_bytes":
                handlerSelector = "v_bytes"
            elif handlerSelector == "v_bytes":   
                print('Getting v-plane bytes')
                v_bytes = message
                print(f"V-plane bytes length : ${len(v_bytes)}")
                handlerSelector = None
                await websocket.send(f"Received v_bytes")
            elif message == "process":
                handlerSelector = "process"
            elif handlerSelector == "process":
                print("Processing the image")
                img = YUVtoRGBO()
                (label, confidence, bbox) = tester.test(img)
                handlerSelector = None
                label_str = None
                if label == 1:
                    label_str = "Real"
                elif label == 2:
                    label_str = "Fake"
                
                jsonString = json.dumps({'label' : f'{label_str}', 'confidence' : f"{"{:.{}f}".format(confidence * 100, 2)}"})
                await websocket.send(jsonString)
                # cv2.imshow("img", img)
                # cv2.waitKey(10)
                # cv2.destroyAllWindows
            else:
                handlerSelector = None
                await websocket.send(f"Reset everything")
                
            


            # rawData = message
            # decodedData = json.loads(rawData)
            # print(decodedData)
            # print(type(decodedData))
            # img = YUVtoRGB(decodedData['y_bytes'], decodedData['u_bytes'],decodedData['v_bytes'],decodedData['width'],decodedData['height'])
            # await websocket.send(f"Received image bytes of length ${len(rawData)}")
            # cv2.imshow("img", img)
            # cv2.waitKey(0)
            # await process_frame(image_bytes)
            # print(f"Received bytes length: {len(image_bytes)}")
            # print(f"Sample bytes: ${image_bytes[:20]}")
            # print(f"Received message: {message}")
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



