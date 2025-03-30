import os
import platform
import ctypes
import subprocess
import sys


def restart_with_admin():
    if platform.system() != 'Windows':
        print("This script requires Windows platform.")
        sys.exit(1)

    if ctypes.windll.shell32.IsUserAnAdmin():
        print("Already running with administrative privileges.")
        return

    script_path = sys.argv[0]
    params = ' '.join([script_path] + sys.argv[1:])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)

    sys.exit(0)


# Restart the script with admin privileges
restart_with_admin()


def extract_arp_cache(save_directory):
    if platform.system() != 'Windows':
        print("This script requires Windows platform.")
        return

    try:
        # Run the arp command to get the ARP cache
        arp_output = subprocess.check_output(['arp', '-a']).decode()

        # Save the ARP cache to a file
        file_path = os.path.join(save_directory, 'arp_cache.txt')
        with open(file_path, 'w') as file:
            file.write(arp_output)

        print(f"ARP cache saved to: {file_path}")

    except subprocess.CalledProcessError as e:
        print(f"Error occurred while extracting ARP cache: {e}")

    except OSError as e:
        print(f"OS Error occurred: {e}")


# Directory where the ARP cache will be saved
save_directory = os.getcwd()

# Extract and save the ARP cache
extract_arp_cache(save_directory)

# Prompt user to press any key before exiting
input("Press any key to exit...")
