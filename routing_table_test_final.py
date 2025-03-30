import subprocess
import platform
import sys
import ctypes
import os

def restart_with_admin():
    if platform.system() != 'Windows':
        print("This script requires the Windows platform.")
        sys.exit(1)

    if ctypes.windll.shell32.IsUserAnAdmin():
        print("Already running with administrative privileges.")
        return

    script_path = sys.argv[0]
    params = ' '.join([script_path] + sys.argv[1:])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)

    sys.exit(0)

def extract_routing_table(output_path):
    system = platform.system()

    if system == "Windows":
        command = "route print"
    elif system == "Linux" or system == "Darwin":
        command = "netstat -rn"
    else:
        print("Unsupported operating system.")
        return

    try:
        routing_table = subprocess.check_output(command, shell=True, universal_newlines=True)
        with open(output_path, "w") as file:
            file.write(routing_table)
        print("Routing table saved to:", output_path)
    except subprocess.CalledProcessError as e:
        print("Error executing the command:", e)
    except IOError as e:
        print("Error writing to file:", e)
    except Exception as e:
        print("An error occurred:", e)

# Specify the desired output path and filename
output_path = os.getcwd()

try:
    # Restart the script with admin privileges
    restart_with_admin()

    # Call the function to extract and save the routing table
    extract_routing_table(output_path)
except Exception as e:
    print("An error occurred:", e)

# Prompt the user to press any key to exit the program
if platform.system() == "Windows":
    import msvcrt
    print("Press any key to exit...")
    msvcrt.getch()
else:
    input("Press Enter to exit...")
