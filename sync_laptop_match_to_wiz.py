import asyncio
import json
import math
import signal
from pathlib import Path

import mss
from PIL import Image, ImageStat
from pywizlight import wizlight, PilotBuilder

RUNNING = True


def stop_handler(*_):
    global RUNNING
    RUNNING = False


def load_config():
    with open(Path(__file__).with_name("config.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def clamp(value, low, high):
    return max(low, min(high, value))


def color_distance(a, b):
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


def get_capture_box(sct, cfg):
    monitor_index = cfg["screen"].get("monitor_index", 1)
    monitors = sct.monitors
    if monitor_index >= len(monitors):
        monitor_index = 1
    mon = monitors[monitor_index]
    crop = cfg["screen"].get("crop", {})

    left = mon["left"] + int(mon["width"] * crop.get("left_percent", 0) / 100)
    top = mon["top"] + int(mon["height"] * crop.get("top_percent", 0) / 100)
    width = int(mon["width"] * crop.get("width_percent", 100) / 100)
    height = int(mon["height"] * crop.get("height_percent", 100) / 100)

    return {
        "left": left,
        "top": top,
        "width": clamp(width, 1, mon["width"]),
        "height": clamp(height, 1, mon["height"]),
    }


def average_screen_color(sct, box, cfg):
    shot = sct.grab(box)
    img = Image.frombytes("RGB", shot.size, shot.rgb)
    img = img.resize((cfg["screen"].get("sample_width", 64), cfg["screen"].get("sample_height", 36)))
    stat = ImageStat.Stat(img)
    r, g, b = [int(x) for x in stat.mean[:3]]

    # Avoid pure black frames making the room useless during replays/loading screens.
    if cfg["light"].get("warm_white_when_dark", True) and (r + g + b) < 45:
        return (255, 180, 80)
    return (r, g, b)


async def set_all_bulbs(bulbs, rgb, brightness):
    r, g, b = rgb
    pilot = PilotBuilder(rgb=(r, g, b), brightness=brightness)
    await asyncio.gather(*(bulb.turn_on(pilot) for bulb in bulbs), return_exceptions=True)


async def main():
    cfg = load_config()
    bulb_ips = cfg.get("bulb_ips", [])
    if not bulb_ips or bulb_ips == ["192.168.1.50"]:
        print("Edit config.json and put your WiZ bulb IP address in bulb_ips first.")
        print("Run: python find_wiz_bulbs.py")
        return

    bulbs = [wizlight(ip) for ip in bulb_ips]
    brightness = cfg["light"].get("brightness", 80)
    interval = cfg["light"].get("update_interval_seconds", 0.25)
    min_change = cfg["light"].get("min_color_change", 12)

    signal.signal(signal.SIGINT, stop_handler)
    signal.signal(signal.SIGTERM, stop_handler)

    previous = None
    with mss.mss() as sct:
        box = get_capture_box(sct, cfg)
        print("Sync started. Play the match fullscreen on your laptop. Press Ctrl+C to stop.")
        while RUNNING:
            rgb = average_screen_color(sct, box, cfg)
            if previous is None or color_distance(rgb, previous) >= min_change:
                await set_all_bulbs(bulbs, rgb, brightness)
                previous = rgb
            await asyncio.sleep(interval)

    print("Stopped.")


if __name__ == "__main__":
    asyncio.run(main())
