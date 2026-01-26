"""Python Application To Make The NVIDIA  Driver Ues Fine Power Management"""

import sys
import os
import subprocess

def checkDriver():
    nDriver = subprocess.run(['ls', '/usr/lib/systemd/system'], capture_output=True)  # Gets output from ls /usr/lib
    nDriverOutput = nDriver.stdout       # Gets output from nDriver
    return "nvidia-persistenced" in str(nDriverOutput)  # Check for nvidia in nDriverOutput and returns result

def checkSudo():               
    if(os.geteuid()==0): # Check if the user id is 0, if it is, then running as sudo
        return True
    
    else:
        return False

def createRules():
    with open('/lib/udev/rules.d/80-nvidia-pm.rules', 'a') as nvidiapm:
        for i in nvidiapm:
            if(i=='ACTION=="bind", SUBSYSTEM=="pci", ATTR{vendor}=="0x10de", ATTR{class}=="0x030000", TEST=="power/control", ATTR{power/control}="auto"'):
                print("Power Management Rules Are Already In Place")
                return

            else:
                nvidiapm.write('# Enable runtime PM for NVIDIA VGA/3D controller devices on driver bind')
                nvidiapm.write('ACTION=="bind", SUBSYSTEM=="pci", ATTR{vendor}=="0x10de", ATTR{class}=="0x030000", TEST=="power/control", ATTR{power/control}="auto"')
                nvidiapm.write('ACTION=="bind", SUBSYSTEM=="pci", ATTR{vendor}=="0x10de", ATTR{class}=="0x030200", TEST=="power/control", ATTR{power/control}="auto"')
                nvidiapm.write(' ')
                nvidiapm.write('# Disable runtime PM for NVIDIA VGA/3D controller devices on driver unbind')
                nvidiapm.write('ACTION=="unbind", SUBSYSTEM=="pci", ATTR{vendor}=="0x10de", ATTR{class}=="0x030000", TEST=="power/control", ATTR{power/control}="on"')
                nvidiapm.write('ACTION=="unbind", SUBSYSTEM=="pci", ATTR{vendor}=="0x10de", ATTR{class}=="0x030200", TEST=="power/control", ATTR{power/control}="on"')
                print('Created Power Management Rules')
                return

def main():

# Prints The Opening Screen To Show Script Requirements
    print("   |-------------------------------------------------------|")
    print("   |     NVIDIA - ENABLE FINE-GRAINED POWER MANAGEMENT     |")
    print("   |-------------------------------------------------------|")
    print("   | REQUIREMENTS:                                         |")
    print("   | 1) Have the NVIDIA Proprietary Driver Installed       |")
    print("   | 2) This Script Must Have Sudo Privileges              |")
    print("   |-------------------------------------------------------|")
    print("   | REQUIREMENTS MET:                                     |")

# Check The Requirements Met
    driverStatus = checkDriver()  # Sets driverStatus to true if NVIDIA driver is installed
    if driverStatus:
        print("   | 1) NVIDIA DRIVER: INSTALLED                           |")

    else:
        print("   | 1) NVIDIA DRIVER: NOT INSTALLED                       |")
        print("   |-------------------------------------------------------| \n")
        sys.exit(1)

    sudoStatus = checkSudo()  # Set sudoStatus to true if running with root permissions
    if sudoStatus:
        print("   | 2) SUDO PRIVILEGES: TRUE                              |")
    else:
        print("   | 2) SUDO PRIVILEGES: FALSE                             |")
        print("   |-------------------------------------------------------| \n")
        sys.exit(1)
    
    print("   |-------------------------------------------------------| \n")

# Continue Once Requirements Have Been Met
    continueResult = input('Continue With NVIDIA Power Management Configuration (y/n): ')

    if(continueResult=='y' or continueResult=='Y'):
        print('Creating /lib/udev/rules.d/80-nvidia-pm.rules')
        createRules()

    
if __name__ == "__main__":
# This block ensures the main function runs when the script is executed
# but not when it's imported as a module.
    try:
         main()
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)