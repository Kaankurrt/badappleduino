# badappleduino

video streaming for ssd1306 oled displays using arduino as a serial bridge.

this project implements a pc-driven video player that streams 1-bit frames to a 128x64 ssd1306 display. video frames are processed, thresholded, run-length encoded, and sent over high-speed serial. originally optimized for bad apple playback, but works with arbitrary video files.

# demo video

[<img src="https://i.ytimg.com/vi/zpJZMAIo5Sw/maxresdefault.jpg" width="50%">](https://www.youtube.com/watch?v=zpJZMAIo5Sw "BAD APPLE ON ARDUINO V2!")

## features

- realtime video streaming to ssd1306 (128x64)
- 1-bit grayscale conversion with adjustable threshold
- run-length encoding to reduce serial bandwidth
- 0xAA handshake-based frame synchronization
- optional realtime fps sync to original video
- audio extraction and playback (via moviepy + pygame)
- loop mode and frame-accurate seeking
- live oled preview on host pc
- designed for very high baud rates (default: 2,000,000)
- realtime sync and frame integrity

## realtime sync and frame integrity
in v2.0.0, a toggle for "realtime sync" is implemented to handle the audio-visual drift. when enabled, the engine calculates the expected frame based on the system clock and skips (drops) processed frames if the hardware (arduino/oled) lags behind. when disabled, the engine forces the display of every single frame, ensuring perfect visual continuity (frame integrity) at the cost of losing synchronization with the audio over time.

## performance disclaimer

this project is fundamentally limited by hardware constraints.

the ssd1306 operates over i2c, which is typically limited to ~800khz. 

all frame data must travel from the host pc over serial, be decoded by a 16mhz microcontroller, and then forwarded to the display. 

complex scenes significantly reduce effective throughput.

as a result:
- framerate is variable
- fast or noisy scenes may slow down playback
- slow-motion effects are expected
- perfect realtime playback is not guaranteed, even with sync enabled

this is a hardware-bound limitation, not a software bug.

## requirements

### hardware

- arduino (uno, nano, or compatible 16mhz avr)
- ssd1306 128x64 oled display (i2c)
- wiring:
  - sda -> a4
  - scl -> a5
- usb connection to host pc

### software

- python 3.x
- opencv-python
- pyserial
- numpy
- pillow
- pygame
- moviepy 
## setup

1. flash the corresponding arduino sketch (.ino) that:
   - initializes the ssd1306
   - sends 0xAA to request each frame
   - decodes rle frame data
2. install python dependencies listed above. 
```bash
pip install opencv-python pyserial numpy pillow pygame moviepy
```
3. connect the arduino and oled display.
4. launch the python application.
5. select a video file (mp4, avi, mkv).

if moviepy is available, audio will be extracted automatically and synced during playback.

## usage

```bash
python player.py (or player_VX_X_X.py)
```
select the serial port, verify baud rate (default: 2000000), choose a video file, then start streaming.

the arduino requests each frame by sending the byte 0xAA. 

upon receiving this handshake, the host sends a run-length encoded framebuffer. 

very high baud rates are used to minimize latency, which may expose usb-serial limitations depending on hardware quality.

## notes

best results are achieved with high-contrast source videos

lowering threshold noise improves rle compression

usb-to-serial adapters vary significantly in reliability at 2m baud

this project is not intended for production use

## contributing

issues should be opened before pull requests to discuss changes. 
keep code style consistent with the existing codebase. experimental optimizations and hardware-specific hacks are welcome, but should be documented clearly.

## PLEASE GIVE CREDITS.

### if you have any questions, feel free to open an issue or send me an email

```bash
ktekapps@gmail.com
```

made by wdibt ^.^
