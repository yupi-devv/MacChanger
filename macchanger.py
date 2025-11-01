#!/usr/bin/python3
import argparse
import os
import random
import re
import subprocess
import sys


def get_default_gateway_linux():
    """Get default network interface"""
    try:
        with open("/proc/net/route") as f:
            for line in f:
                fields = line.strip().split()
                if fields[1] == "00000000" and int(fields[3], 16) & 2:
                    return fields[0]  # Interface name
    except Exception:
        print("Cannot get default interface on this system, can't read /proc/net/route")
        return None


def get_active_interfaces():
    """Get only UP/active interfaces"""
    try:
        result = subprocess.check_output(["ip", "link", "show", "up"]).decode()
        interfaces = []

        for line in result.split("\n"):
            match = re.match(r"^\d+:\s+(\S+):", line)
            if match:
                iface = match.group(1).split("@")[0]
                if iface != "lo":
                    interfaces.append(iface)

        return interfaces
    except subprocess.CalledProcessError:
        return []


def get_mac_with_ip(interface: str):
    """Get MAC address using ip command"""
    try:
        result = subprocess.check_output(["ip", "link", "show", interface]).decode()
        mac = re.search(r"link/ether\s+([\da-f:]+)", result, re.IGNORECASE)
        if mac:
            return mac.group(1)
    except subprocess.CalledProcessError:
        return None


def get_all_mac_addresses_ip():
    """Get all MAC addresses using ip command"""
    try:
        result = subprocess.check_output(["ip", "link", "show"]).decode()
        mac_list = re.findall(r"link/ether\s+([\da-f:]+)", result, re.IGNORECASE)
        return mac_list
    except subprocess.CalledProcessError:
        return []


def validate_mac_address(mac: str) -> bool:
    """
    Validate MAC address format

    Args:
        mac: MAC address string to validate

    Returns:
        True if valid, False otherwise
    """
    # Regular expression pattern for validating MAC address (with : or -)
    mac_pattern = r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"
    return bool(re.match(mac_pattern, mac))


def generate_random_mac() -> str:
    """
    Generate a random MAC address

    Returns:
        Random MAC address in format XX:XX:XX:XX:XX:XX
    """
    # Start with 00 to ensure it's a locally administered address
    mac = [
        0x00,
        0x16,
        0x3E,
        random.randint(0x00, 0x7F),
        random.randint(0x00, 0xFF),
        random.randint(0x00, 0xFF),
    ]

    return ":".join(map(lambda x: "%02x" % x, mac))


def change_mac_address(
    interface: str | None = None,
    current_mac_address: str | None = None,
    new_mac_address: str | None = None,
):
    """
    Change MAC address of network interface

    Args:
        interface: Network interface name (e.g., eth0, wlan0)
        current_mac_address: Current MAC address (for verification)
        new_mac_address: New MAC address to set
    """
    if interface is None:
        interface = get_default_gateway_linux()
        if interface is None:
            print("[-] Error: Could not automatically determine default interface.")
            return False
    elif isinstance(interface, str):
        system_interfaces = get_active_interfaces()
        if interface not in system_interfaces:
            print(
                f"[-] Error: Interface '{interface}' not found in system or not active!"
            )
            print(f"[*] Available interfaces: {', '.join(system_interfaces)}")
            return False
    else:
        print(
            "[-] Error: The default interface could not be determined automatically and it is not specified as an argument."
        )
        return False

    if current_mac_address is None:
        current_mac_address = get_mac_with_ip(interface)
        if current_mac_address is None:
            print(f"[-] Error: Cannot find MAC address for interface '{interface}'")
            return False
    elif isinstance(current_mac_address, str):
        current_mac_address_onif = get_mac_with_ip(interface)
        if (
            current_mac_address_onif is None
            or current_mac_address != current_mac_address_onif
        ):
            print(
                f"[-] Error: MAC address verification failed for interface '{interface}'"
            )
            print(
                f"[*] Expected: {current_mac_address}, Found: {current_mac_address_onif}"
            )
            return False
    else:
        print("[-] Error: Invalid current MAC address type")
        return False

    if new_mac_address is None:
        new_mac_address = generate_random_mac()
        print(f"[*] Generated random MAC address: {new_mac_address}")
    else:
        if not validate_mac_address(new_mac_address):
            print(f"[-] Error: Invalid MAC address format: {new_mac_address}")
            print(
                "[*] MAC address must be in format: XX:XX:XX:XX:XX:XX or XX-XX-XX-XX-XX-XX"
            )
            return False
        new_mac_address = new_mac_address.replace("-", ":")

    print("\n" + "=" * 50)
    print(f"[+] Network Interface: {interface}")
    print(f"[+] Current MAC Address: {current_mac_address}")
    print(f"[+] New MAC Address: {new_mac_address}")
    print("=" * 50 + "\n")

    try:
        print("[*] Bringing interface down...")
        subprocess.run(
            ["ip", "link", "set", interface, "down"], check=True, capture_output=True
        )

        print(f"[*] Changing MAC address to {new_mac_address}...")
        subprocess.run(
            ["ip", "link", "set", interface, "address", new_mac_address],
            check=True,
            capture_output=True,
        )

        print("[*] Bringing interface up...")
        subprocess.run(
            ["ip", "link", "set", interface, "up"], check=True, capture_output=True
        )

        verify_mac = get_mac_with_ip(interface)
        if verify_mac and verify_mac.lower() == new_mac_address.lower():
            print("\n[OK] SUCCESS: MAC address changed successfully!")
            print(f"[OK] Verified MAC address: {verify_mac}")
            return True
        else:
            print("\n[!] WARNING: MAC address change may have failed")
            print(f"[!] Expected: {new_mac_address}, Got: {verify_mac}")
            return False

    except subprocess.CalledProcessError as e:
        print("\n[-] ERROR: Failed to change MAC address")
        print(f"[-] Command error: {e}")
        if e.stderr:
            print(f"[-] Details: {e.stderr.decode().strip()}")
        return False
    except Exception as e:
        print(f"\n[-] ERROR: Unexpected error occurred: {e}")
        return False


def main():
    """Main function with argument parsing"""
    if os.geteuid() != 0:
        print("=" * 60)
        print("[!] ROOT PRIVILEGES REQUIRED")
        print("=" * 60)
        print("This program requires root privileges to modify network interfaces.")
        print("\nPlease run this script with sudo:")
        print("  sudo ./your-script-name -h")
        print("=" * 60)
        sys.exit(1)

    parser = argparse.ArgumentParser(
        prog="MacChanger",
        description="Simple utility to change MAC address on Linux systems",
        epilog="Example: sudo ./your-script-name.py -i eth0 -n 00:11:22:33:44:55",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-i",
        "--interface",
        type=str,
        metavar="INTERFACE",
        help="Network interface to change (e.g., eth0, wlan0). If not specified, uses default gateway interface",
    )

    parser.add_argument(
        "-n",
        "--new-mac",
        type=str,
        metavar="MAC",
        dest="new_mac_address",
        help="New MAC address in format XX:XX:XX:XX:XX:XX or XX-XX-XX-XX-XX-XX",
    )

    parser.add_argument(
        "-c",
        "--current-mac",
        type=str,
        metavar="MAC",
        dest="current_mac_address",
        help="Current MAC address for verification (optional)",
    )

    parser.add_argument(
        "-r",
        "--random",
        action="store_true",
        help="Generate and set a random MAC address",
    )

    parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="List all active network interfaces and their MAC addresses",
    )

    args = parser.parse_args()

    if args.list:
        print("\n" + "=" * 60)
        print("ACTIVE NETWORK INTERFACES")
        print("=" * 60)
        interfaces = get_active_interfaces()
        if not interfaces:
            print("[-] No active interfaces found")
        else:
            for iface in interfaces:
                mac = get_mac_with_ip(iface)
                print(f"  {iface:15} -> {mac if mac else 'N/A'}")
        print("=" * 60 + "\n")
        sys.exit(0)

    if args.random:
        args.new_mac_address = None

    success = change_mac_address(
        interface=args.interface,
        current_mac_address=args.current_mac_address,
        new_mac_address=args.new_mac_address,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
