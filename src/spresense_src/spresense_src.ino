#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME680.h>
#include "BLE1507.h"
#include <Servo.h>

// BME680のI2Cアドレス
#define BME680_I2C_ADDRESS 0x77

// BLEのUUID
#define UUID_SERVICE  0x3802
#define UUID_CHAR     0x4a02

// BLE関連
static BT_ADDR addr = {{0x19, 0x84, 0x06, 0x14, 0xAB, 0xCD}};
static char ble_name[BT_NAME_LEN] = "SPR-PERIPHERAL";
BLE1507 *ble1507;

// BME680センサーインスタンス
Adafruit_BME680 bme;

Servo myServo; // サーボモータのインスタンス
const int servoPin = 5; // サーボモータ制御用のピン (Spresense拡張ボードのピン)

void setup() {
  // シリアルモニタの初期化
  Serial.begin(115200);
  while (!Serial) delay(10);

  // BME680センサーの初期化
  Serial.println("Initializing BME680...");
  if (!bme.begin(BME680_I2C_ADDRESS)) {
    Serial.println("BME680 not found! Check wiring.");
    while (1);
  }
  Serial.println("BME680 initialized.");
  
  bme.setTemperatureOversampling(BME680_OS_8X);
  bme.setHumidityOversampling(BME680_OS_2X);
  bme.setPressureOversampling(BME680_OS_4X);
  bme.setIIRFilterSize(BME680_FILTER_SIZE_3);
  bme.setGasHeater(320, 150);

  // BLE1507の初期化
  Serial.println("Initializing BLE...");
  ble1507 = BLE1507::getInstance();
  if (ble1507 == nullptr) {
    Serial.println("Failed to get BLE instance.");
    while (1);
  }

  if (!ble1507->beginPeripheral(ble_name, addr, UUID_SERVICE, UUID_CHAR)) {
    Serial.println("Failed to initialize BLE peripheral.");
    while (1);
  }

  if (!ble1507->startAdvertise()) {
    Serial.println("Failed to start BLE advertising.");
    while (1);
  }

  Serial.println("BLE initialized and advertising started.");

  myServo.attach(servoPin, 500, 2400);
  // 初期角度設定
  myServo.write(5);
  Serial.println("Servo motor control started");
}

void loop() {
  // BME680センサーデータを読み取る
  if (!bme.performReading()) {
    Serial.println("Failed to read sensor data.");
    return;
  }

  // センサーデータをBLEで送信
  char bleData[20];
  snprintf(bleData, sizeof(bleData),
           "Gas:%.2fkOhm",
           bme.gas_resistance / 1000.0);

  ble1507->writeNotify((uint8_t*)bleData, strlen(bleData));

  if( (bme.gas_resistance / 1000.0) <= 90.0 ){
    myServo.write(175);
  }

  // デバッグ出力
  Serial.println(bleData);

  // 1秒間待機
  delay(1000);
}
