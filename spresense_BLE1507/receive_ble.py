import asyncio
from bleak import BleakClient, BleakScanner
from bleak.exc import BleakError

DEVICE_NAME = "SPR-PERIPHERAL"  # デバイス名
CHAR_UUID = "00004a02-0000-1000-8000-00805f9b34fb"  # キャラクタリスティックUUID

def notification_handler(sender, data):
    """通知を処理するハンドラー"""
    print(f"Notification from {sender}: {data.decode('utf-8')}")

async def main():
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

    print(f"Attempting to connect to device {spresence_device.name} ({spresence_device.address})...")
    try:
        async with BleakClient(spresence_device) as client:
            if not client.is_connected:
                print("Failed to connect to device")
                return
            print("Connected to device")

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

if __name__ == "__main__":
    asyncio.run(main())