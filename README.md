# NVIDIA Power Management

A small Python utility for Linux that configures the NVIDIA proprietary driver to use **fine-grained (dynamic) runtime power management**, reducing idle power draw on systems with an NVIDIA GPU.

It does this by writing the necessary `udev` and `modprobe` configuration files that NVIDIA's driver looks for, then enabling the `nvidia-persistenced` service.

## What It Does

When run, the script:

1. **Checks prerequisites**
   - Confirms the NVIDIA proprietary driver is installed (by checking for `nvidia-persistenced` under `/usr/lib/systemd/system`).
   - Confirms the script is being run with `sudo`/root privileges.
2. **Creates udev rules** — `/lib/udev/rules.d/80-nvidia-pm.rules`
   Adds rules that set `power/control` to `auto` when the NVIDIA VGA/3D controller binds to its driver, and back to `on` when it unbinds. This allows the GPU to runtime-suspend when idle.
3. **Creates modprobe options** — `/etc/modprobe.d/nvidia.conf`
   Adds `options nvidia "NVreg_DynamicPowerManagement=0x02"` to enable fine-grained dynamic power management at the driver level. Optionally also adds `options nvidia "NVreg_EnableGpuFirmware=0"` if you choose to (this can help on systems where the open GSP firmware interferes with power management).
4. **Enables `nvidia-persistenced`**
   Runs `systemctl enable nvidia-persistenced` so persistence mode is managed automatically on boot.

If any of the rules are already present in the target files, the script detects that and skips re-adding them.

## Requirements

- Linux system with the **NVIDIA proprietary driver** installed
- `sudo` / root privileges (required to write to `/lib/udev/rules.d/` and `/etc/modprobe.d/`, and to manage the `nvidia-persistenced` service)
- Python 3

## Usage

```bash
sudo python3 "NVIDIA Power Management.py"
```

The script will print a requirements check, then prompt for confirmation before making any changes:

```
 |-------------------------------------------------------|
 |       NVIDIA - ENABLE FINE-GRAINED POWER MANAGEMENT    |
 |-------------------------------------------------------|
 |  REQUIREMENTS:                                         |
 |  1) Have the NVIDIA Proprietary Driver Installed       |
 |  2) This Script Must Have Sudo Privileges               |
 |-------------------------------------------------------|
 |  REQUIREMENTS MET:                                      |
 |  1) NVIDIA DRIVER: INSTALLED                            |
 |  2) SUDO PRIVILEGES: TRUE                               |
 |-------------------------------------------------------|

Continue With NVIDIA Power Management Configuration (y/n):
```

After confirming, you'll optionally be asked whether to also add the `NVreg_EnableGpuFirmware=0` modprobe option.

**A reboot is required** after running the script for the new udev rules and modprobe options to take effect.

## Files Modified

| File | Purpose |
|---|---|
| `/lib/udev/rules.d/80-nvidia-pm.rules` | Runtime PM udev rules for the NVIDIA PCI device |
| `/etc/modprobe.d/nvidia.conf` | Driver module options enabling dynamic power management |
| `nvidia-persistenced.service` | Enabled via `systemctl` so persistence mode runs at boot |

## Notes / Limitations

- The script exits without making changes if the NVIDIA driver isn't detected or if it isn't run with sudo.
- It assumes `/lib/udev/rules.d/80-nvidia-pm.rules` and `/etc/modprobe.d/nvidia.conf` already exist on disk (e.g. as empty files) before it tries to read/append to them — create them first if they aren't already present on your system.
- Tested on systems using the NVIDIA proprietary driver; behavior with the open-source `nouveau` driver is not supported.
- Always review the resulting configuration files before rebooting, especially if you have an existing custom power management setup.

## License

No license specified yet — add one (e.g. MIT) if you'd like others to freely use or contribute to this project.
