import asyncio
import websockets
import numpy as np
import base64
import cv2
import json
import tester


# handlerSelector = None
# width = None
# height = None
# y_bytes = None
# u_bytes = None
# v_bytes = None
# y_bpp = None
# u_bpp = None
# v_bpp = None

client_data = {}

# async def process_frame(frame_data):
#     # Decode base64 image
#     # image_data = base64.b64decode(frame_data)
#     nparr = np.frombuffer(frame_data, np.uint8)
#     print(nparr[:20])
#     print(f"np array shape: {nparr.shape[0]}")
#     img = nparr.reshape((480, 720))
#     # img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    
#     if img is not None:
#         print("Showing the image")
#         # Display the frame
#         # cv2.imshow('Frame', img)
#         # if cv2.waitKey(1) & 0xFF == ord('q'):
#             # return False
#     else:
#         print("Image is empty")
#     return True


# def YUVtoRGB():
#     global handlerSelector, width, height, y_bytes, y_bpp, u_bpp, u_bytes, v_bpp, v_bytes, u_bpp, u_bytes

#     Y = np.frombuffer(y_bytes, np.uint8)
#     # img = y_nparr.reshape((width, height))
#     # Y = np.array(y_bytes)
#     Y = np.reshape(Y, (height,width))
#     print(f"Y-size: ${Y.shape}")

#     V = np.frombuffer(v_bytes, np.uint8)
#     # V = np.repeat(V, 2, 0)
#     padlength = (width//2 * height) - V.shape[0]
#     print(f"v pad length: {padlength}")
#     V = np.pad(V, (0, padlength), 'constant', constant_values=0)
#     V = np.reshape(V, (height//2,width))
#     V = np.repeat(V, 2, 0)
#     print(f"V-size: ${V.shape}")

#     # U = np.array(u_bytes)
#     U = np.frombuffer(u_bytes, np.uint8)
#     # U = np.repeat(U, 2, 0)
#     padlength = (width//2 * height) - U.shape[0]
#     print(f"u pad length: {padlength}")
#     U = np.pad(U, (0, padlength), 'constant', constant_values=0)
#     U = np.reshape(U, (height//2,width))
#     U = np.repeat(U, 2, 0)
#     print(f"U-size: ${U.shape}")

#     RGBMatrix = (np.dstack([Y,V, U])).astype(np.uint8)
#     RGBMatrix = cv2.cvtColor(RGBMatrix, cv2.COLOR_YUV2BGR, 3)

#     RGBMatrix = cv2.rotate(RGBMatrix, cv2.ROTATE_90_COUNTERCLOCKWISE)
#     print(f"final image size: ${RGBMatrix.shape}")
#     return RGBMatrix

def YUVtoRGBO(y_bytes, u_bytes, v_bytes, width, height):
    # global handlerSelector, width, height, y_bytes, y_bpp, u_bpp, u_bytes, v_bpp, v_bytes, u_bpp, u_bytes

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
    # global handlerSelector, width, height, y_bytes, y_bpp, u_bpp, u_bytes, v_bpp, v_bytes, u_bpp, u_bytes
    print("Client connected")
    try:
        async for message in websocket:
            # print(len(message))
            data = message
            client_id = data[:20].decode('ascii')
            total_parts = 4
            part_index = data[20]
            part_data = data[21:]
            print(f"Rec: Part index: {part_index}, Total parts: {total_parts}, Client id: {client_id}, Part data length: {len(part_data)}")
            
            # data = json.loads(message)
            # client_id = data['client_id']
            # total_parts = data['total_parts']
            # part_index = data['part_index']
            # part_data = data['part_data']
            
            # Initialize storage for client if not present
            if client_id not in client_data:
                client_data[client_id] = {'parts': [None] * total_parts, 'received_count': 0}
            
            client_data[client_id]['parts'][part_index] = part_data
            client_data[client_id]['received_count'] += 1
            
            # Check if all parts have been received
            if client_data[client_id]['received_count'] == total_parts:
                # extract data parts
                # extract metadata idx = 0
                metadata = json.loads(client_data[client_id]['parts'][0].decode('utf-8'))
                # metadata = client_data[client_id]['parts'][0]
                width = metadata['width']
                height = metadata['height']
                y_bpp = metadata['y_bpp']
                u_bpp = metadata['u_bpp']
                v_bpp = metadata['v_bpp']
                print(f"width: {width}, height: {height}, y_bpp: {y_bpp}")
                y_bytes = client_data[client_id]['parts'][1]
                u_bytes = client_data[client_id]['parts'][2]
                v_bytes = client_data[client_id]['parts'][3]
                print("Processing the image")
                img = YUVtoRGBO(y_bytes, u_bytes, v_bytes, width, height)
                test_result = tester.test(img)

                label_str = None
                if test_result is None:
                    jsonString = json.dumps({'label' : "No Face", 'confidence' :"0"})
                    await websocket.send(jsonString)
                else:
                    (label, confidence, bbox) = test_result

                    if label == 1:
                        label_str = "Real"
                    elif label == 2:
                        label_str = "Fake"
                    
                    jsonString = json.dumps({'label' : f'{label_str}', 'confidence' : "{:.{}f}".format(confidence * 100, 2)})
                    await websocket.send(jsonString)

                del client_data[client_id]

                # cv2.imshow("img", img)
                # cv2.waitKey(10)
                # cv2.destroyAllWindows

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



