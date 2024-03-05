import socket
import cv2
import numpy as np


def receive_video():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('192.168.86.55', 5000))  # Listen on all network interfaces, port 12345
    server_socket.listen(1)
    print("Waiting for connection...")
    client_socket, addr = server_socket.accept()
    print(f"Connection from {addr}")

    data = b""
    try:
        while True:
            packet = client_socket.recv(4096)
            if not packet:
                break
            data += packet
            # Check if we have a full frame
            while b'\xff\xd9' in data:  # JPEG end of frame marker
                # Split at the end of the frame
                frame_data, data = data.split(b'\xff\xd9', 1)
                frame_data += b'\xff\xd9'

                # Decode the frame
                frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)
                if frame is not None:
                    cv2.imshow('Frame', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
    finally:
        client_socket.close()
        server_socket.close()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    receive_video()
