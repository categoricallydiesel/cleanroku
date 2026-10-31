#!/usr/bin/env python3
"""Find Roku devices on your Wi-Fi and audit them for bloat.

Uses Roku's External Control Protocol (ECP, port 8060). Standard library only.

  python3 roku_scan.py                 # discover Rokus and list installed channels
  python3 roku_scan.py --ip 192.168.1.50   # skip discovery, query one device
  python3 roku_scan.py --keep "Netflix,YouTube,Plex"   # flag everything else as removable

If discovery finds nothing: Roku Settings > System > Advanced system settings >
Control by mobile apps > Network access must be "Default" or "Permissive".
"""
import argparse
import re
import socket
import urllib.request
import xml.etree.ElementTree as ET

SSDP_ADDR = ("239.255.255.250", 1900)
SSDP_QUERY = (
    "M-SEARCH * HTTP/1.1\r\n"
    "Host: 239.255.255.250:1900\r\n"
    'Man: "ssdp:discover"\r\n'
    "ST: roku:ecp\r\n"
    "MX: 3\r\n\r\n"
)

# Channels Roku preinstalls or pushes that most people never open.
KNOWN_BLOAT = {
    "The Roku Channel", "Roku Media Player", "Live TV", "Prime Video",
    "Peacock TV", "Paramount Plus", "Pluto TV", "Tubi", "Sling TV",
    "Spotify", "Apple TV", "Max", "Disney Plus", "Hulu", "Philo",
    "fuboTV", "Frndly TV", "Sports", "What to Watch",
}


def discover(timeout=4):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    sock.settimeout(timeout)
    for _ in range(2):
        sock.sendto(SSDP_QUERY.encode(), SSDP_ADDR)
    found = set()
    try:
        while True:
            data, _ = sock.recvfrom(4096)
            m = re.search(r"(?im)^location:\s*(\S+)", data.decode(errors="ignore"))
            if m:
                found.add(m.group(1).rstrip("/"))
    except socket.timeout:
        pass
    return sorted(found)


def get(base, path):
    with urllib.request.urlopen(f"{base}{path}", timeout=5) as r:
        return ET.fromstring(r.read())


def report(base, keep):
    info = get(base, "/query/device-info")
    field = lambda k: (info.findtext(k) or "?").strip()
    print(f"\n=== {field('user-device-name') or field('friendly-device-name')} @ {base}")
    print(f"Model: {field('model-name')} ({field('model-number')})  "
          f"OS: {field('software-version')}  Roku TV: {field('is-tv')}")

    apps = get(base, "/query/apps")
    channels = [(a.get("id"), a.get("type"), (a.text or "").strip()) for a in apps]
    print(f"\n{len(channels)} installed channels:")
    for cid, ctype, name in sorted(channels, key=lambda c: c[2].lower()):
        if keep is not None:
            tag = "keep" if name.lower() in keep else "REMOVE?"
        else:
            tag = "likely bloat" if name in KNOWN_BLOAT else ""
        print(f"  [{tag:>12}] {name:<40} id={cid} ({ctype})")
    print("\nRemove a channel: highlight it on the home screen, press * on the remote, "
          "choose Remove channel. (Roku does not allow removal over the network.)")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ip", help="Roku IP address (skips discovery)")
    p.add_argument("--keep", help="Comma separated channel names you want to keep")
    args = p.parse_args()
    keep = {k.strip().lower() for k in args.keep.split(",")} if args.keep else None

    bases = [f"http://{args.ip}:8060"] if args.ip else discover()
    if not bases:
        print("No Roku found. Check that this computer is on the same Wi-Fi as the Roku "
              "and that Control by mobile apps is set to Default or Permissive.")
        return 1
    for base in bases:
        try:
            report(base, keep)
        except Exception as e:  # noqa: BLE001
            print(f"\n{base}: could not query ({e}). Check Control by mobile apps setting.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
