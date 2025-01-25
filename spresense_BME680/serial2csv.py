import serial
import csv
import time

# シリアルポートの設定
COM_PORT = "COM4"  # シリアルポート
BAUD_RATE = 115200  # Arduinoで設定したボーレート
CSV_FILE = "sensor_data.csv"  # 保存するCSVファイル名

def parse_sensor_data(line):
    """
    シリアルデータを解析して数値を抽出する関数。
    """
    try:
        if "温度" in line:
            return "Temperature", float(line.split(":")[1].replace("°C", "").strip())
        elif "湿度" in line:
            return "Humidity", float(line.split(":")[1].replace("%", "").strip())
        elif "気圧" in line:
            return "Pressure", float(line.split(":")[1].replace("hPa", "").strip())
        elif "ガス抵抗値" in line:
            return "Gas Resistance", float(line.split(":")[1].replace("kOhms", "").strip())
    except Exception as e:
        print(f"データ解析エラー: {e}")
    return None, None

def main():
    try:
        # シリアルポートを開く
        ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
        print(f"シリアルポート {COM_PORT} に接続しました。データを待機中...")

        # CSVファイルを開く（追記モード）
        with open(CSV_FILE, mode="w", newline="") as file:
            writer = csv.writer(file)

            # CSVヘッダー行
            writer.writerow(["Timestamp", "Temperature (°C)", "Humidity (%)", "Pressure (hPa)", "Gas Resistance (kOhms)"])

            # データ格納用辞書
            sensor_data = {
                "Temperature": None,
                "Humidity": None,
                "Pressure": None,
                "Gas Resistance": None
            }

            while True:
                # シリアルからデータを読み取る
                line = ser.readline().decode("utf-8").strip()
                if line:
                    print(f"受信データ: {line}")

                    # データ解析
                    key, value = parse_sensor_data(line)
                    if key and value is not None:
                        sensor_data[key] = value

                    # 全てのデータが揃ったらCSVに書き込む
                    if all(sensor_data.values()):
                        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                        writer.writerow([
                            timestamp,
                            sensor_data["Temperature"],
                            sensor_data["Humidity"],
                            sensor_data["Pressure"],
                            sensor_data["Gas Resistance"]
                        ])
                        print(f"CSVに書き込み: {sensor_data}")

                        # データをリセット
                        sensor_data = {key: None for key in sensor_data}

    except serial.SerialException as e:
        print(f"シリアルポートのエラー: {e}")
    except KeyboardInterrupt:
        print("\nプログラムを終了します。")
    finally:
        # シリアルポートを閉じる
        ser.close()
        print("シリアルポートを閉じました。")

if __name__ == "__main__":
    main()
