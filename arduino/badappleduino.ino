#include <Wire.h>

#define OLED_ADDR 0x3C
#define FRAME_SIZE 1024

uint8_t frame[FRAME_SIZE];

// send a single command byte to the oled
void cmd(uint8_t c) {
  Wire.beginTransmission(OLED_ADDR);
  Wire.write(0x00);
  Wire.write(c);
  Wire.endTransmission();
}

// standard ssd1306 init sequence 
void oledInit() {
  cmd(0xAE);          // display off
  cmd(0xD5); cmd(0x80); // set osc freq
  cmd(0xA8); cmd(0x3F); // mux ratio
  cmd(0xD3); cmd(0x00); // display offset
  cmd(0x40);          // start line
  cmd(0x8D); cmd(0x14); // charge pump
  cmd(0x20); cmd(0x00); // horizontal addressing
  cmd(0xA1);          // remap columns
  cmd(0xC8);          // scan direction
  cmd(0xDA); cmd(0x12); // hardware config
  cmd(0x81); cmd(0xCF); // set contrast
  cmd(0xD9); cmd(0xF1); // pre-charge
  cmd(0xDB); cmd(0x40); // vcomh deselect
  cmd(0xA4);          // resume from ram
  cmd(0xA6);          // normal mode (not inverted)
  cmd(0xAF);          // display on
}

// push the buffer to the oled page by page
void drawFrame(uint8_t *buf) {
  for (uint8_t page = 0; page < 8; page++) {
    cmd(0xB0 + page); // set page address
    cmd(0x00);        // set lower col addr
    cmd(0x10);        // set higher col addr

    for (uint8_t col = 0; col < 128; col += 16) {
      Wire.beginTransmission(OLED_ADDR);
      Wire.write(0x40); // switch to data stream

      for (uint8_t i = 0; i < 16; i++) {
        Wire.write(buf[page * 128 + col + i]);
      }

      Wire.endTransmission();
    }
  }
}

void setup() {
  Serial.begin(2000000);   // crank it up to 2m baud for speed
  Wire.begin();
  Wire.setClock(800000);   // boost i2c clock to 800khz

  oledInit();
}

void loop() {
  // ping python that we are ready for the next frame
  Serial.write(0xAA);

  // suck in the 1024 byte frame from serial
  size_t idx = 0;
  while (idx < FRAME_SIZE) {
    if (Serial.available()) {
      frame[idx++] = Serial.read();
    }
  }

  // dump buffer to display
  drawFrame(frame);

  // frame processing done, signal ack
  Serial.write(0x55);
}
