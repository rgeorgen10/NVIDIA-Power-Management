"""Python Application To Make The NVIDIA  Driver Ues Fine Power Management"""

import sys
import subprocess

def checkDriver():
    nDriver = subprocess.run(['ls', '/usr/lib'], capture_output=True)  # Gets output from ls /usr/lib
    nDriverOutput = nDriver.stdout       # Gets output from nDriver
    return "nvidia" in str(nDriverOutput)  # Check for nvidia in nDriverOutput and returns result

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
    print("   | 1) ")


# Check The Requirements Met
    driverStatus = checkDriver()  # Sets driverStatus to true if NVIDIA driver is installed
    print(driverStatus) 
    
if __name__ == "__main__":
# This block ensures the main function runs when the script is executed
# but not when it's imported as a module.
    try:
         main()
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)