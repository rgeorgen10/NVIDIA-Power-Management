import sys
import os
import subprocess
from pathlib import Path
import textwrap
import re

# file path variables
UDEVPATH = '/lib/udev/rules.d/'
UDEVFILE = UDEVPATH + '80-nvidia-pm.rules'
MODPROBEPATH = '/etc/modprobe.d/'
MPFILE = MODPROBEPATH + 'nvidia.conf'

# Change color to green
def green():
    print('\033[32m', end='')
# Change color to default
def white():
    print('\033[0m', end='')

# Check if the NVIDIA driver is installed
def checkDriver():
    return Path('/usr/lib/systemd/system/nvidia-persistenced.service').exists()  # Check if the nvidia-persistenced service file exists

# Check if the script has Sudo permission
def checkSudo():               
    return os.geteuid()==0  # Check if the user id is 0, if it is, then running as sudo

# Create all the required directories if they don't exist
def createpath(path):
    Path(path).mkdir(parents=True, exist_ok=True)

def enableService():
    # Enable the nvidia-persistenced service
    subprocess.run(['systemctl', 'enable', 'nvidia-persistenced'], check=True)
    subprocess.run(['systemctl', 'start', 'nvidia-persistenced'], check=True)
    print("Enabled and started nvidia-persistenced service")

# Function to create the udev rules
def createUdevRules():
    udevrules = textwrap.dedent("""\
    # Enable runtime PM for NVIDIA VGA/3D controller devices on driver bind
    ACTION=="bind", SUBSYSTEM=="pci", ATTR{vendor}=="0x10de", ATTR{class}=="0x030000", TEST=="power/control", ATTR{power/control}="auto"
    ACTION=="bind", SUBSYSTEM=="pci", ATTR{vendor}=="0x10de", ATTR{class}=="0x030200", TEST=="power/control", ATTR{power/control}="auto"

    # Disable runtime PM for NVIDIA VGA/3D controller devices on driver unbind
    ACTION=="unbind", SUBSYSTEM=="pci", ATTR{vendor}=="0x10de", ATTR{class}=="0x030000", TEST=="power/control", ATTR{power/control}="on"
    ACTION=="unbind", SUBSYSTEM=="pci", ATTR{vendor}=="0x10de", ATTR{class}=="0x030200", TEST=="power/control", ATTR{power/control}="on"
    """)

    # First, make sure the directory is created
    createpath(UDEVPATH)

    # Check if the udevfile exists
    if(os.path.exists(UDEVFILE)):
        with open(UDEVFILE, 'r') as file:
            if udevrules in file.read():
                print("UDEV rules already present")
                file.close()
                return

    # Otherwise, create the file
    with open(UDEVFILE, 'a') as file:
        file.write(udevrules)
        print("UDEV rules have been created in %s" % (UDEVFILE))
        file.close()
        return

# function to create the nvidia.conf file
def createConf():
    finePower = 'options nvidia "NVreg_DynamicPowerManagement=0x02"'
    newerVersion = 'options nvidia "NVreg_DynamicPowerManagement=0x03"'
    extraRule = 'options nvidia "NVreg_EnableGpuFirmware=0"'
    writepm = True
    writeExtra = True

    # Check directory
    createpath(MODPROBEPATH)

    # Check if udevfile exists and check for existing rules
    if(os.path.exists(MPFILE)):
        # Check what rules have already been written to the file
        with open(MPFILE, 'r') as file:
            contents = file.read()
            if re.search("NVreg_DynamicPowerManagement=0x0[23]", contents):
                print("Modprobe file already has fine-grained power management enabled!")
                writepm = False
            if re.search("NVreg_EnableGpuFirmware=0", contents):
                print("Modprobe file already has the extra rule!")
                writeExtra = False

    # Write fine grained power management rules
    if writepm:
        pmSet = pmPrompt()
        with open(MPFILE, 'a') as file:
            if pmSet == 1: file.write(finePower+'\n')
            if pmSet == 2: file.write(newerVersion+'\n')
            print("Power management mode written to modprobe file in %s" % (MPFILE))

    # Write extra rule prompting first
    if writeExtra:
        if userPrompt("Would you like to add the extra rule to disable GPU firmware. Only works with the proprietary driver (y/n): "):
            with open(MPFILE, 'a') as file:
                file.write(extraRule+'\n')
                print("Extra rule written to modprobe file in %s" % (MPFILE))
        else:
            print("Extra rule not added to modprobe file")

    file.close()
    return 

# Get user y/n input
def userPrompt(text):
    while(True):    
        val = input(text)
        if val.lower() == 'y': return True
        if val.lower() == 'n': return False
        print("\033[1A\033[2K\r", end='')

# Get which power management rule to add
def pmPrompt():
    print("\n   Select a power management flag based on your GPU")
    print("   1. 0x02 - For Turing generation GPUs")
    print("   2. 0x03 - For Ampere and newer generation GPUs")
    print("  -------------------------------------------------------")
    while(True):
        val = input("Enter 1 or 2 to select: ")
        if val == '1': return 1
        if val == '2': return 2
        print("\033[1A\033[2K\r", end='') # Not a valid input, ask again
    
# Print opening program
def requirements():
    green()
    print("   |-------------------------------------------------------|")
    print("   |     NVIDIA - ENABLE FINE-GRAINED POWER MANAGEMENT     |")
    print("   |-------------------------------------------------------|")
    print("   | REQUIREMENTS:                                         |")
    print("   | 1) Have the NVIDIA Driver Installed                   |")
    print("   | 2) This Script Must Have Sudo Privileges              |")
    print("   |-------------------------------------------------------|")
    print("   | REQUIREMENTS MET:                                     |")
    print("   | 1) NVIDIA Driver: Installed                           |") if checkDriver() else print("   | 1) NVIDIA Driver: Not Installed                       |")
    print("   | 2) Sudo Priviledges: True                              |") if checkSudo() else print("   | 2) Sudo Priviledges: False                             |")
    print("   |-------------------------------------------------------|")
    print('')
    if not checkDriver() or not checkSudo(): print("         Exiting Script: Requirements Not Met!!!"); return False
    return True

# Main program operation
def main():
    # Check the requirements
    if not requirements(): white(); sys.exit(1)

    # Prompt to configure udev rules
    if not userPrompt("Would you like to configure the UDEV rules (y/n): "): print("Script Terminated By User"); white(); sys.exit(0)

    # Configure udev rules
    createUdevRules()

    # configure nvidia.conf
    createConf()

    # Enable nvidia-persistenced service
    enableService()

    # Print completion message
    print("\n   |-------------------------------------------------------|")
    print("   |     NVIDIA FINE-GRAINED POWER MANAGEMENT CONFIGURED   |")
    print("   |-------------------------------------------------------|")
    print("   | Post steps:                                           |")
    print("   | 1) Rebuild initramfs                                  |")
    print("   | 2) Reboot your system to apply changes                |")
    print("   |-------------------------------------------------------|")

    # Make terminal white again
    white()

# Launch main
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        white()
        sys.exit(1)