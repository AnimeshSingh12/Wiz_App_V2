# WiZ Match Light Sync

This syncs your WiZ light color with whatever match is playing on your laptop screen.
It does not need the WiZ Sports Live cloud feature. It samples the laptop screen and sends the average color to the WiZ bulb over Wi-Fi.

## Setup

1. Install Python 3.10 or newer.
2. Connect laptop and WiZ bulb to the same Wi-Fi.
3. Open this folder in Terminal / Command Prompt.
4. Install requirements:

```bash
pip install -r requirements.txt
```

## Find your bulb IP

Run:

```bash
python find_wiz_bulbs.py
```

Copy the IP address shown.

If discovery fails, get the IP from your router app or WiZ device/network details.

## Configure

Open `config.json` and replace:

```json
"192.168.1.50"
```

with your real WiZ bulb IP.

Example:

```json
"bulb_ips": ["192.168.1.9"]
```

For multiple bulbs:

```json
"bulb_ips": ["192.168.1.23", "192.168.1.9"]
```

## Run sync

Play the match on your laptop, preferably fullscreen, then run:

```bash
python sync_laptop_match_to_wiz.py
```

Stop with Ctrl+C.

## Tuning

In `config.json`:

- `brightness`: light brightness from 10 to 100.
- `update_interval_seconds`: lower means faster updates. 0.25 is safe.
- `min_color_change`: higher means less flicker.
- `crop`: restrict capture area if scoreboard/ads dominate the color.

## Common fixes

### Bulb not changing

- Laptop and bulb must be on same Wi-Fi.
- Disable VPN.
- Allow Python through Windows firewall.
- Confirm bulb IP is correct.

### Too much flicker

Increase:

```json
"min_color_change": 25
```

or increase:

```json
"update_interval_seconds": 0.5
```

### Colors look too random

Crop only the video area. Example for center screen:

```json
"crop": {
  "left_percent": 10,
  "top_percent": 10,
  "width_percent": 80,
  "height_percent": 80
}
```
