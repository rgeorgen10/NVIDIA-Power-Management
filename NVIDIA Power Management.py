"""Python Application To Make The NVIDIA  Driver Ues Fine Power Management"""

import sys
import os
import subprocess

def checkDriver():
    # '''Checks if the nvidia driver is installed'''
    nDriver = subprocess.run(['ls', '/usr/lib/systemd/system'], capture_output=True)  # Gets output from ls /usr/lib
    nDriverOutput = nDriver.stdout       # Gets output from nDriver
    return "nvidia-persistenced" in str(nDriverOutput)  # Check for nvidia in nDriverOutput and returns result

def checkSudo():               
    # '''Check if user is running as sudo'''
    if(os.geteuid()==0): # Check if the user id is 0, if it is, then running as sudo
        return True
    
    else:
        return False

def createRules(): # Creades 80-nvidia-pm.rules
    with open('/lib/udev/rules.d/80-nvidia-pm.rules') as nvidiapm: # Opens file to read
        for j in nvidiapm: 
            if(j=='ACTION=="bind", SUBSYSTEM=="pci", ATTR{vendor}=="0x10de", ATTR{class}=="0x030000", TEST=="power/control", ATTR{power/control}="auto"\n'): # check if power management rules are in place
                print("Power Management Rules Are Already In Place")
                return

    with open('/lib/udev/rules.d/80-nvidia-pm.rules', 'a') as nvidiapmwrite: # open file to write
        nvidiapmwrite.write('# Enable runtime PM for NVIDIA VGA/3D controller devices on driver bind\n')  # add power management rules
        nvidiapmwrite.write('ACTION=="bind", SUBSYSTEM=="pci", ATTR{vendor}=="0x10de", ATTR{class}=="0x030000", TEST=="power/control", ATTR{power/control}="auto"\n')
        nvidiapmwrite.write('ACTION=="bind", SUBSYSTEM=="pci", ATTR{vendor}=="0x10de", ATTR{class}=="0x030200", TEST=="power/control", ATTR{power/control}="auto"\n')
        nvidiapmwrite.write(' \n')
        nvidiapmwrite.write('# Disable runtime PM for NVIDIA VGA/3D controller devices on driver unbind\n')
        nvidiapmwrite.write('ACTION=="unbind", SUBSYSTEM=="pci", ATTR{vendor}=="0x10de", ATTR{class}=="0x030000", TEST=="power/control", ATTR{power/control}="on"\n')
        nvidiapmwrite.write('ACTION=="unbind", SUBSYSTEM=="pci", ATTR{vendor}=="0x10de", ATTR{class}=="0x030200", TEST=="power/control", ATTR{power/control}="on"\n')
        nvidiapmwrite.write(' \n')
        nvidiapmwrite.write('# Enable runtime PM for NVIDIA VGA/3D controller devices on adding device\n')
        nvidiapmwrite.write('ACTION=="add", SUBSYSTEM=="pci", ATTR{vendor}=="0x10de", ATTR{class}=="0x030000", TEST=="power/control", ATTR{power/control}="auto"\n')
        nvidiapmwrite.write('ACTION=="add", SUBSYSTEM=="pci", ATTR{vendor}=="0x10de", ATTR{class}=="0x030200", TEST=="power/control", ATTR{power/control}="auto"\n')
        print('Created Power Management Rules')
        return

def createModprobe(): #Add modprobe rules
    with open('/etc/modprobe.d/nvidia.conf') as modproberead: # open file to read
        for i in modproberead:
            if(i=='options nvidia "NVreg_DynamicPowerManagement=0x02"\n'): # checks if modprobe rule is in place
                print('Modprobe File for Nvidia Already In Place')
                addExtraRule = input('Do You also want to add "options nvidia "NVreg_EnableGpuFirmware=0"" (y/n): ') # Check if user wants to add additonal rule
                if(addExtraRule=='y' or addExtraRule=='Y'): 
                    for j in modproberead:
                        if(j=='options nvidia "NVreg_EnableGpuFirmware=0"\n'): # check if additional rules is in place
                            print('options nvidia "NVreg_EnableGpuFirmware=0" is already in place')
                            return

                    with open('/etc/modprobe.d/nvidia.conf', 'a') as modprobewrite: # open file to write
                        modprobewrite.write('options nvidia "NVreg_EnableGpuFirmware=0"\n') # add aditional rules
                        print('Added options nvidia "NVreg_EnableGpuFirmware=0"\n')
                        return
    
    # if modprobe rules hasn't already been added
    with open('/etc/modprobe.d/nvidia.conf') as modprobewrite: # open file to write
        modprobewrite.write('options nvidia "NVreg_DynamicPowerManagement=0x02"')  # add modrpobe rule
        print('Created Modprobe Rules')
        addExtraRule = input('Do You also want to add "options nvidia "NVreg_EnableGpuFirmware=0"" (y/n): ') # prompt if user wants to add aditional rules
        if(addExtraRule=='y' or addExtraRule=='Y'):
            for j in modproberead:
                if(j=='options nvidia "NVreg_EnableGpuFirmware=0"\n'):
                    print('options nvidia "NVreg_EnableGpuFirmware=0" is already in place') 
                    return

            modprobewrite.write('options nvidia "NVreg_EnableGpuFirmware=0"\n') # write additional rule if already not in place
            print('Added options nvidia "NVreg_EnableGpuFirmware=0"\n')
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
        print('Creating /etc/modprobe.d/nvidia.conf')
        createModprobe()
        print('Enabling nvidia-persistenced')
        subprocess.run(['systemctl', 'enable', 'nvidia-persistenced'])
        print(' ')
        print('NVIDIA power management rules have been added! Reboot the system for the rules to go into effect.')


    
if __name__ == "__main__":
# This block ensures the main function runs when the script is executed
# but not when it's imported as a module.
    try:
         main()
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)