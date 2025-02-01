import asyncio
import threading
import tkinter as tk
from bleak import BleakClient, BleakScanner
from bleak.exc import BleakError

DEVICE_NAME = "SPR-PERIPHERAL"  # SPRESENSEのBLEデバイス名
CHAR_UUID = "00004a02-0000-1000-8000-00805f9b34fb"  # キャラクタリスティックUUID

class GasSensorGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Gas Sensor GUI")

        # ガスセンサの値を表示するラベル
        self.label_value = tk.Label(self.master, text="ガスセンサ値: ---", font=("", 16))
        self.label_value.pack(pady=10)

        # 90以下のときに表示するラベル
        self.label_warning = tk.Label(self.master, text="", font=("", 16), fg="red")
        self.label_warning.pack(pady=10)

        # 接続開始ボタン
        self.button_connect = tk.Button(self.master, text="BLE接続開始", command=self.start_ble_thread, font=("", 14))
        self.button_connect.pack(pady=10)

        # 終了ボタン（不要であれば省略可）
        self.button_quit = tk.Button(self.master, text="終了", command=self.master.destroy, font=("", 14))
        self.button_quit.pack(pady=10)

        # BLEスレッド用のフラグ
        self.ble_thread_running = False
        self.ble_thread = None

    def start_ble_thread(self):
        """BLE処理を別スレッドで開始する"""
        if not self.ble_thread_running:
            self.ble_thread_running = True
            self.ble_thread = threading.Thread(target=self.run_ble_loop, daemon=True)
            self.ble_thread.start()
            self.button_connect.config(state=tk.DISABLED)  # 二重起動防止のためボタンを無効化

    def run_ble_loop(self):
        """asyncioのイベントループを実行する"""
        asyncio.run(self.ble_main())

    async def ble_main(self):
        """BLEデバイスをスキャン＆接続し、通知を受信するメイン処理"""
        print("Scanning for BLE devices...")
        devices = await BleakScanner.discover()
        spresence_device = None
        for device in devices:
            print(f"Found device: {device.name} ({device.address})")
            if device.name == DEVICE_NAME:
                spresence_device = device
                break

        if spresence_device is None:
            print(f"Device with name {DEVICE_NAME} not found. Ensure SPRESENCE is advertising.")
            return

        print(f"Attempting to connect to {spresence_device.name} ({spresence_device.address})...")
        try:
            async with BleakClient(spresence_device) as client:
                if not client.is_connected:
                    print("Failed to connect to device")
                    return
                print("Connected to device")

                # キャラクタリスティック通知を有効化
                await client.start_notify(CHAR_UUID, self.notification_handler)
                print("Started receiving notifications...")

                # 通知受信を待機（適宜変更）
                while self.ble_thread_running:
                    await asyncio.sleep(0.1)

                # 通知を無効化
                await client.stop_notify(CHAR_UUID)
                print("Stopped receiving notifications")
        except BleakError as e:
            print(f"BLE Error: {e}")

    def notification_handler(self, sender, data):
        """BLE通知を受け取った際のコールバック"""
        text = data.decode("utf-8")  # 例: "Gas:12.34kOhm"
        # 値を取り出す(単純な文字列処理例)
        # "Gas:" と "kOhm" を取り除き数値に変換
        value_str = text.replace("Gas:", "").replace("kOhm", "")
        try:
            gas_value = float(value_str)
        except ValueError:
            return  # パースエラー時は無視

        # メインスレッド上のGUIを更新するため、afterを使う
        self.master.after(0, self.update_sensor_value, gas_value)

    def update_sensor_value(self, gas_value):
        """ガスセンサの値を画面に反映"""
        self.label_value.config(text=f"ガスセンサ値: {gas_value:.2f}")

        if gas_value <= 90:
            self.label_warning.config(text="ガスに注意")
        else:
            self.label_warning.config(text="")

    def on_closing(self):
        """ウィンドウが閉じられるときの処理"""
        self.ble_thread_running = False
        self.master.destroy()


def main():
    root = tk.Tk()
    app = GasSensorGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
