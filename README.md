badappleduino - video streaming for ssd1306 & arduino
=====================================================

demo video

this project lets you stream any video from your pc to an oled display via an arduino. while optimized for the legendary 'bad apple' video, it supports custom resolutions and works with any mp4/avi file through a specialized python-to-arduino bridge.

--- how it works ---

(THIS IS THE README OF THE V2. V1 IS NOT AVAILABLE ANYMORE.)

the system uses a producer-consumer architecture:

python captures video frames, resizes them based on your config, and applies b/w thresholding.

data is compressed using run-length encoding (rle) to minimize serial traffic.

a hardware handshake protocol (0xaa) ensures the arduino is ready before the next frame is sent.

audio is automatically extracted and synced using the system clock.

--- performance warning / disclaimer ---

heads up: the fps will be variable. don't expect the smoothest 30fps experience.

why is it lagging? the bottlenecks are purely hardware-related (arduino side):

i2c bus limits: even at 800khz, pushing a full frame (e.g., 1024 bytes for 128x64) to the oled takes time.

serial processing: arduino has to manage incoming 2m baud serial data and redirect it to the i2c bus.

cpu clock: the 16mhz atmega328p is doing its best, but handling high-speed serial + i2c bit-banging is heavy work.

expect some "stuttering" or "rubber-banding" depending on how fast the arduino can clear its buffer.

--- hardware ---

arduino (uno [i tried a nano clone too but it didnt work])

ssd1306 oled (supports 128x64, 128x32 or custom sizes)

wiring:

vcc -> 5v

gnd -> gnd

scl -> a5 (on uno/nano)

sda -> a4 (on uno/nano)


--- setup ---

flash the badapple.ino to your arduino.

make sure you have python 3.12+ installed.

install dependencies: pip install opencv-python pyserial pillow numpy pygame moviepy

select your video file via the gui.

identify your serial port (e.g., 'com3' or '/dev/ttyusb0').

--- run ---

python player.pyw

the script uses a handshake system (0xaa) to keep the python sender and arduino receiver in sync. 

it won't fix the low fps, but it prevents the screen from glitching out into static garbage. 

(note: random pixels can appear because of extreme 2m baud rate signal noise.)
