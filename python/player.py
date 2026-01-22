import cv2
import serial
import time
from PIL import Image
import numpy as np

# global configs
SERIAL_PORT = 'COM8'
BAUD_RATE = 2000000
VIDEO_FILE = 'bad_apple.mp4'

# init serial connection
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=None)
    print(f"connected to: {SERIAL_PORT}")
    time.sleep(2)  # wait for arduino to reboot after opening port
except Exception as e:
    print(f"serial port error: {e}")
    exit()

# open the video file
cap = cv2.VideoCapture(VIDEO_FILE)

print("video playing... ctrl+c to kill")

try:
    while cap.isOpened():
        # wait for the 0xaa handshake from arduino
        ready_signal = ser.read(1)
        if ready_signal != b'\xAA':
            continue

        # grab next frame
        ret, frame = cap.read()
        if not ret:
            print("video ended.")
            break

        # image processing: gray -> resize -> dither
        # move from opencv bgr to pil world
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        pil_img = Image.fromarray(gray_frame)
        
        # lanczos looks the best for downscaling bad apple
        # convert('1') handles the dithering/thresholding
        img = pil_img.resize((128, 64), Image.Resampling.LANCZOS).convert('1')
        
        # get raw pixel data (0 or 255)
        pixels = list(img.getdata())
        
        # pack bits into ssd1306 vertical byte format
        buffer = bytearray(1024)
        for page in range(8):
            for col in range(128):
                val = 0
                for bit in range(8):
                    y = page * 8 + bit
                    # if pixel is white, set the corresponding bit
                    if pixels[y * 128 + col]: 
                        val |= (1 << bit)
                buffer[page * 128 + col] = val

        # blast the frame buffer to the serial port
        ser.write(buffer)

        # wait for the 0x55 ack to keep things in sync
        # helps preventing frame tearing and buffer overflows
        done_signal = ser.read(1)
        if done_signal != b'\x55':
            print("sync lost!")

except KeyboardInterrupt:
    print("\ninterrupted by user.")

finally:
    # release resources
    cap.release()
    ser.close()
    print("cleanup done.")
