import sys
import os
import subprocess

# file path variables
UDEVPATH = '/lib/udev/rules.d/'
UDEVFILE = UDEVPATH + '80-nvidia-pm.conf'
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

# Check filepath
def createpath(path):
    if os.path.isdir(path):
    if os.path.

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


# Launch main
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occured: {e}", file=sys.stderr)
        sys.exit(1)