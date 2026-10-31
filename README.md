# cleanroku

Find your Roku on Wi-Fi, list what's installed and strip out as much bloat, tracking and advertising as Roku allows.

## The honest limits

Roku is a locked platform. Firmware is signed, the bootloader is locked and there is no ADB. That means:

- No custom OS and no replacement home screen. An Apple TV-style launcher is not possible on Roku.
- Channels can't be removed over the network. You remove them with the remote.
- The sponsored tile on the home screen can't be removed.

If you want the full [cleanyourtv](https://github.com/Gathin23/cleanyourtv) experience (debloat plus Apple TV-style home), you need an Android TV or Google TV device. A Google TV Streamer or Onn 4K box is cheap and works with it.

## Step 1: Find your Roku and audit it

Run this on a computer on the same Wi-Fi as the Roku (Python 3, no installs needed):

```bash
python3 roku_scan.py
python3 roku_scan.py --keep "Netflix,YouTube,Plex"   # flags everything else as REMOVE?
python3 roku_scan.py --ip 192.168.1.50               # if discovery fails
```

If nothing is found: Settings > System > Advanced system settings > Control by mobile apps > Network access = Default or Permissive.

## Step 2: Remove channels

On the home screen, highlight each channel marked REMOVE?, press `*` on the remote, choose Remove channel.

## Step 3: Turn off tracking and ads

Menu names shift a little between Roku OS versions.

- Settings > Privacy > Advertising: turn off personalized ads / turn on Limit ad tracking, and reset the advertising ID.
- Settings > Privacy > Smart TV experience: turn off Use info from TV inputs (Roku TVs only; this is the screen-content tracking).
- Settings > Privacy > Voice / Microphone: set channel microphone access to Never.
- Settings > Home screen: hide menu items you don't use (What to Watch, Live TV, Sports, Movie Store, TV Store and similar).
- Settings > Theme > Screensaver: pick a plain clock or turn it off to avoid sponsored screensavers.
- Settings > Home screen > Start-up input (Roku TVs): set to your last-used input so it doesn't boot to the ad-heavy home.

## Step 4 (optional): Network-level blocking

A DNS blocker like Pi-hole or NextDNS can cut some Roku ads and telemetry. Block selectively: blanket-blocking Roku domains can break updates and the channel store.
