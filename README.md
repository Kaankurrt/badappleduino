
badappleduino - video streaming for ssd1306 & arduino
=====================================================


## Demo Video
[![Watch the demo](https://img.youtube.com/vi/GT6FCmWX1Uk/0.jpg)](https://www.youtube.com/watch?v=GT6FCmWX1Uk)




this project lets you stream any video from your pc to a 
128x64 oled display via an arduino. it's optimized for 
the legendary 'bad apple' video but technically works with 
any mp4/avi file.

--- PERFORMANCE WARNING / DISCLAIMER ---

heads up: the video will be SLOW and the FPS will be VARIABLE. 
don't expect a smooth 30fps (even 20fps) experience. (no frame dropping just slow-mo like video)

why is it lagging?
the bottlenecks are purely hardware-related (arduino side):
1. i2c bus limits: even at 800khz, pushing 1024 bytes (one full 
   frame) to the oled takes time.
2. serial processing: arduino has to manage the incoming 
   high-speed serial data and redirect it to the i2c bus.
3. cpu clock: the 16mhz atmega328p is doing its best, but 
   handling 2m baud serial + i2c bit-banging is heavy work.

expect some "stuttering" or "rubber-banding" depending on 
how fast the arduino can clear its buffer.

--- HARDWARE ---

* arduino (uno/nano/pro mini)
* ssd1306 oled (128x64) (0.96 inch)
* wiring:
  - vcc -> 5v
  - gnd -> gnd
  - scl -> a5 (on uno/nano)
  - sda -> a4 (on uno/nano)

--- SETUP ---

1. flash the badapple.ino to your arduino.
2. make sure you have python installed.
3. install dependencies: 
   pip install opencv-python pyserial pillow numpy
4. put your video file (name it bad_apple.mp4) in the same folder.
5. update the SERIAL_PORT in the python script (e.g., 'COM8').

--- RUN ---

python main.py

the script uses a handshake system (0xAA/0x55) to keep the 
python sender and arduino receiver in sync. it won't fix 
the low fps, but it prevents the screen from glitching out 
into static garbage.(but random pixels can appear because of 2m baud.)
