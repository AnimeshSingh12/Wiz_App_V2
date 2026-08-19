import asyncio
from pywizlight.discovery import discover_lights

async def main():
    bulbs = await discover_lights(broadcast_space="192.168.1.255")
    if not bulbs:
        print("No WiZ bulbs found. Check that laptop and bulb are on the same Wi-Fi.")
        return
    print("Found WiZ bulbs:")
    for bulb in bulbs:
        print(f"- IP: {bulb.ip}")

if __name__ == "__main__":
    asyncio.run(main())
