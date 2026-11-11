import sys
import os
import subprocess
from pathlib import Path
import textwrap

# file path variables
UDEVPATH = '/home/riley/code/'
UDEVFILE = UDEVPATH + '80-nvidia-pm.rules'
MODPROBEPATH = 'etc/modprobe.d'
MPFILE = MODPROBEPATH + 'nvidia.conf'

# Change color to green
def green():
    print('\033[32m', end='')
# Change color to default
def white():
    print('\033[0m', end='')

# Check if the NVIDIA driver is installed
def checkDriver():
    nDriver = subprocess.run(['ls', '/usr/lib/systemd/system'], capture_output=True)  # Gets output from ls /usr/lib
    nDriverOutput = nDriver.stdout       # Gets output from nDriver
    return "nvidia-persistenced" in str(nDriverOutput)  # Check for nvidia in nDriverOutput and returns result

# Check if the script has Sudo permission
def checkSudo():               
    return os.geteuid()==0  # Check if the user id is 0, if it is, then running as sudo

# Create all the required directories if they don't exist
def createpath(path):
    Path(path).mkdir(parents=True, exist_ok=True)

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
                return

    # Otherwise, create the file
    with open(UDEVFILE, 'w') as file:
        file.write(udevrules)
        print("UDEV rules have been created in %s" % (UDEVFILE))
        return

# function to create the nvidia.conf file
    def createConf():
        finePower = 'options nvidia "NVreg_DynamicPowerManagement=0x02"'
        newerVersion = 'options nvidia "NVreg_DynamicPowerManagement=0x03"'
        extraRule = 'options nvidia "NVreg_EnableGpuFirmware=0"'

        # Check directory
        createpath(MODPROBEPATH)

        # Check if udevfile exists and check for existing rules
        if(os.path.exists(MPFILE)):
            with open(MPFILE, 'r') as file:
                if finePower in file.read() and newerVersion in file.read() or extraRule in file.read():
                    print("Modprobe file already has fine-grained power management enabled!")

# Get user y/n input
def userPrompt(text):
    while(True):    
        val = input(text)
        if val.lower() == 'y': return True
        if val.lower() == 'n': return False
        print("\033[1A\033[2K\r", end='')
    
# Print opening program
def requirements():
    green()
    print("   |-------------------------------------------------------|")
    print("   |     NVIDIA - ENABLE FINE-GRAINED POWER MANAGEMENT     |")
    print("   |-------------------------------------------------------|")
    print("   | REQUIREMENTS:                                         |")
    print("   | 1) Have the NVIDIA Proprietary Driver Installed       |")
    print("   | 2) This Script Must Have Sudo Privileges              |")
    print("   |-------------------------------------------------------|")
    print("   | REQUIREMENTS MET:                                     |")
    print("   | 1) NVIDIA Driver: Installed                           |") if checkDriver() else print("   | 1) NVIDIA Driver: Not Installed                       |")
    print("   | 2) Sudo Prviledges: True                              |") if checkSudo() else print("   | 2) Sudo Prviledges: False                             |")
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


# Launch main
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occured: {e}", file=sys.stderr)
        sys.exit(1)