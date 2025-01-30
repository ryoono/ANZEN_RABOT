#include <Servo.h>

Servo myServo; // サーボモータのインスタンス
const int servoPin = 5; // サーボモータ制御用のピン (Spresense拡張ボードのピン)

void setup() {
  myServo.attach(servoPin, 500, 2400);

  // 初期角度設定
  myServo.write(5);

  Serial.begin(115200);
  Serial.println("Servo motor control started");

  delay(10000); // 10秒停止
}

void loop() {

  myServo.write(130); // 180度に設定
}
