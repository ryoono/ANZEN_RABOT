#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME680.h>

// BME680のI2Cアドレス（通常は0x76か0x77）
#define BME680_I2C_ADDRESS 0x77

// BME680センサーのインスタンスを作成
Adafruit_BME680 bme;

void setup() {
  // シリアルモニタを開始
  Serial.begin(115200);
  while (!Serial) {
    delay(10); // シリアル接続待機
  }

  Serial.println("BME680センサーの初期化を開始します...");

  // センサーの初期化
  if (!bme.begin(BME680_I2C_ADDRESS)) {
    Serial.println("BME680センサーが見つかりません。配線を確認してください。");
    while (1);
  }

  Serial.println("BME680センサーが正常に初期化されました！");

  // センサーの設定
  bme.setTemperatureOversampling(BME680_OS_8X);
  bme.setHumidityOversampling(BME680_OS_2X);
  bme.setPressureOversampling(BME680_OS_4X);
  bme.setIIRFilterSize(BME680_FILTER_SIZE_3);
  bme.setGasHeater(320, 150); // 320°Cで150msのヒーター持続時間
}

void loop() {
  // センサーデータを取得
  if (!bme.performReading()) {
    Serial.println("センサー読み取りエラー！");
    return;
  }

  // ガスデータとその他の環境データを表示
  Serial.print("温度: ");
  Serial.print(bme.temperature);
  Serial.println(" °C");

  Serial.print("湿度: ");
  Serial.print(bme.humidity);
  Serial.println(" %");

  Serial.print("気圧: ");
  Serial.print(bme.pressure / 100.0);
  Serial.println(" hPa");

  Serial.print("ガス抵抗値: ");
  Serial.print(bme.gas_resistance / 1000.0);
  Serial.println(" kOhms");

  Serial.println();

  // 1秒ごとに更新
  delay(1000);
}
