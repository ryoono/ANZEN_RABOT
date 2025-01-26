import asyncio
from bleak import BleakClient, BleakScanner
from bleak.exc import BleakError

DEVICE_NAME = "SPR-GAS-SENSOR"  # SPRESENSEのBLEデバイス名
CHAR_UUID = "00004a02-0000-1000-8000-00805f9b34fb"  # キャラクタリスティックUUID

def notification_handler(sender, data):
    """通知を処理するハンドラー"""
    print(f"Raw notification from {sender}: {data}")  # 生のバイトデータを表示
    try:
        decoded_data = data.decode('utf-8')
        print(f"Decoded notification: {decoded_data}")
    except Exception as e:
        print(f"Error decoding notification data: {e}")

async def main():
    print("Scanning for BLE devices...")
    devices = await BleakScanner.discover()

    if not devices:
        print("No devices found.")
        return

    # スキャン結果を詳細に表示
    print("\n--- Scanned BLE Devices ---")
    for device in devices:
        print(f"Device: {device.name or 'Unknown'} ({device.address}), Metadata: {device.metadata}")
    print("----------------------------\n")

    # SPRESENSEデバイスを特定
    spresence_device = None
    for device in devices:
        if device.name == DEVICE_NAME:
            spresence_device = device
            break

    if spresence_device is None:
        print(f"Device with name '{DEVICE_NAME}' not found. Attempting to connect to the first available device for debugging...")
        if devices:
            spresence_device = devices[0]  # 最初に見つかったデバイスを選択
        else:
            print("No BLE devices available for connection.")
            return

    print(f"Attempting to connect to device: {spresence_device.name or 'Unknown'} ({spresence_device.address})...")
    try:
        async with BleakClient(spresence_device.address) as client:
            if not client.is_connected:
                print("Failed to connect to device")
                return
            print(f"Connected to device: {spresence_device.name or 'Unknown'} ({spresence_device.address})")

            # サービスとキャラクタリスティックをリストアップ
            print("\n--- Device Services and Characteristics ---")
            services = await client.get_services()
            for service in services:
                print(f"Service: {service.uuid}")
                for char in service.characteristics:
                    print(f"  Characteristic: {char.uuid} (Properties: {char.properties})")
            print("-------------------------------------------\n")

            # キャラクタリスティックUUIDが存在するか確認
            if CHAR_UUID not in [char.uuid for service in services for char in service.characteristics]:
                print(f"Characteristic UUID {CHAR_UUID} not found on this device.")
                return

            # 通知を有効化
            await client.start_notify(CHAR_UUID, notification_handler)
            print("Started receiving notifications...")

            # 受信を一定時間待機
            try:
                await asyncio.sleep(60)  # 60秒間受信を待機
            except KeyboardInterrupt:
                print("Stopped by user")

            # 通知を無効化
            await client.stop_notify(CHAR_UUID)
            print("Stopped receiving notifications")
    except BleakError as e:
        print(f"BLE Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
