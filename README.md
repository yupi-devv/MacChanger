# MacChanger

![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)
![Platform](https://img.shields.io/badge/platform-linux-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A simple Python utility to change MAC addresses of network interfaces on Linux systems.

## Requirements

- Linux (any distribution)
- Python 3.10+
- Root privileges
- `ip` utility (iproute2 package)

# Installation

```shell
git clone https://github.com/yupi-devv/MacChanger.git
cd MacChanger/
chmod +x macchanger.py
```


## Usage

```bash
# List active interfaces
sudo ./macchanger.py -l

# Set specific MAC address
sudo ./macchanger.py -i wlan0 -n 00:11:22:33:44:55

# Set random MAC address
sudo ./macchanger.py -i eth0 -r

# Auto-detect interface
sudo ./macchanger.py -n aa:bb:cc:dd:ee:ff

# Show help
sudo ./macchanger.py -h
```


## Options

| Flag | Description |
| :-- | :-- |
| `-i` | Network interface (eth0, wlan0, etc.) |
| `-n` | New MAC address |
| `-r` | Generate random MAC |
| `-c` | Current MAC for verification |
| `-l` | List all interfaces |

## Important Notes

⚠️ **Changes are temporary** - MAC address will revert to original after reboot

⚠️ **Requires root** - always use `sudo`

⚠️ **Interface goes down** - network disconnects for 1-2 seconds during MAC change


## Troubleshooting

**Interface not found:**

```bash
sudo ./macchanger.py -l  # Check available interfaces
```

**Device or resource busy:**

```bash
sudo systemctl stop NetworkManager
# Change MAC
sudo systemctl start NetworkManager
```


**Invalid MAC format:**

```bash
# Correct format: 00:11:22:33:44:55 or 00-11-22-33-44-55
```
## ⚖️ Disclaimer

**By using this software, you acknowledge and agree that:**

1. This tool is provided for **legitimate purposes only**, including:
   - Network administration on systems you own or manage
   - Security testing and research on authorized systems
   - Educational purposes and learning
   - Personal privacy protection on your own devices

2. **You are solely responsible** for:
   - Ensuring all use complies with applicable laws and regulations
   - Obtaining proper authorization before testing any network or system
   - Understanding the legal consequences of unauthorized network access

3. **The author:**
   - Does NOT authorize, endorse, or encourage illegal or unauthorized use
   - Assumes NO LIABILITY for any misuse, damage, or legal consequences
   - Is NOT responsible for any harm caused by this software
   - Does NOT provide legal advice regarding proper use

4. **Legal consequences:**
   - Unauthorized access to computer systems is illegal in most jurisdictions
   - Violating network policies or bypassing security measures may result in criminal or civil liability
   - Use this tool only with explicit permission on systems you own or are authorized to test

**You use this software entirely AT YOUR OWN RISK.**

## License

MIT License - See LICENSE file for details

