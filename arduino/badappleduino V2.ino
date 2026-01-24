//made by wdibt ^.^
#include <Wire.h>

#define OLED_ADDR 0x3C
#define SCR_W 128
#define SCR_H 64
#define BUF_SZ (SCR_W * SCR_H / 8)

uint8_t fb[BUF_SZ]; // frame buffer

// fast command helper
inline void send_cmd(uint8_t c) {
  Wire.beginTransmission(OLED_ADDR);
  Wire.write(0x00);
  Wire.write(c);
  Wire.endTransmission();
}

void oled_init() {
  uint8_t init_cmds[] = {
    0xAE, 0xD5, 0x80, 0xA8, 0x3F, 0xD3, 0x00, 0x40,
    0x8D, 0x14, 0x20, 0x00, 0xA1, 0xC8, 0xDA, 0x12,
    0x81, 0xCF, 0xD9, 0xF1, 0xDB, 0x40, 0xA4, 0xA6, 0xAF
  };
  for(uint8_t i=0; i<sizeof(init_cmds); i++) send_cmd(init_cmds[i]);
}

void blast_frame(uint8_t *data) {
  for (uint8_t p = 0; p < 8; p++) {
    send_cmd(0xB0 + p);
    send_cmd(0x00);
    send_cmd(0x10);
    
    // push in 16b chunks to avoid wire lib overflow
    for (uint8_t c = 0; c < 128; c += 16) {
      Wire.beginTransmission(OLED_ADDR);
      Wire.write(0x40);
      for (uint8_t i = 0; i < 16; i++) {
        Wire.write(data[p * 128 + c + i]);
      }
      Wire.endTransmission();
    }
  }
}

void setup() {
  Serial.begin(2000000);
  Wire.begin();
  Wire.setClock(800000); // oc i2c
  
  oled_init();
  memset(fb, 0, BUF_SZ);
  blast_frame(fb);
}

void loop() {
  Serial.write(0xAA); // sync pulse

  uint16_t idx = 0;
  while (idx < BUF_SZ) {
    if (Serial.available() >= 2) {
      uint8_t count = Serial.read();
      uint8_t val = Serial.read();
      
      // rle unpack
      while(count-- > 0 && idx < BUF_SZ) {
        fb[idx++] = val;
      }
    }
  }

  blast_frame(fb);
  Serial.write(0x55); // ack
}
