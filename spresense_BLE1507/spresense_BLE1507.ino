/*
 * BLE1507_notify.ino
 * Copyright (c) 2024 Yoshinori Oota
 *
 * This is an example of BLE1507
 *
 * This is a free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
 */


/****************************************************************************
 * Included Files
 ****************************************************************************/

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include "BLE1507.h"

/****************************************************************************
 * ble parameters
 ****************************************************************************/
#define UUID_SERVICE  0x3802
#define UUID_CHAR     0x4a02

static BT_ADDR addr = {{0x19, 0x84, 0x06, 0x14, 0xAB, 0xCD}};
static char ble_name[BT_NAME_LEN] = "SPR-PERIPHERAL";

BLE1507 *ble1507;

/****************************************************************************
 * setup function
 ****************************************************************************/
void setup() {
  Serial.begin(115200);
  Serial.println("start");

  ble1507 = BLE1507::getInstance();
  if (ble1507 == nullptr) {
    Serial.println("BLE1507 instance is null");
    while (true);
  }
  Serial.println("BLE1507 instance created");

  delay(100); // スタック初期化のための短い待機時間
  if (!ble1507->beginPeripheral(ble_name, addr, UUID_SERVICE, UUID_CHAR)) {
    Serial.println("beginPeripheral failed");
    while (true);
  }
  Serial.println("beginPeripheral succeeded");

  if (!ble1507->startAdvertise()) {
    Serial.println("startAdvertise failed");
    while (true);
  }
  Serial.println("startAdvertise succeeded");
}

/****************************************************************************
 * loop function
 ****************************************************************************/
void loop() {
  static uint8_t data = 0;
  uint8_t str_data[4] = {0};
  sprintf((char*)str_data, "%03d", data++);
  data %= 100;
  ble1507->writeNotify(str_data, 3);
  printf("raise notify to the central : ");
  printf("%s\n", str_data);
  sleep(1);
}
