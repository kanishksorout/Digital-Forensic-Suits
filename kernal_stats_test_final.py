import os
import psutil
import platform
import ctypes
import sys

# Function to restart the script with admin privileges
def restart_with_admin():
    if platform.system() != 'Windows':
        print("This script requires Windows platform.")
        return

    if ctypes.windll.shell32.IsUserAnAdmin():
        print("Already running with administrative privileges.")
        return

    script_path = sys.argv[0]
    params = ' '.join([script_path] + sys.argv[1:])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)

    sys.exit(0)

# Restart the script with admin privileges
restart_with_admin()

# Define the output directory
output_directory = os.getcwd()

# Create the output directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)

# Define the output file paths
process_thread_info_path = os.path.join(output_directory, "p_n_t_info.txt")
network_connections_path = os.path.join(output_directory, "net_conc.txt")
file_system_metadata_path = os.path.join(output_directory, "f_s_metadata.txt")
memory_usage_path = os.path.join(output_directory, "mem_usage.txt")

try:
    # Extract and save process and thread information
    with open(process_thread_info_path, 'w') as file:
        for proc in psutil.process_iter(['pid', 'name', 'username', 'create_time', 'status', 'ppid']):
            file.write(f"Process ID (PID): {proc.info['pid']}\n")
            file.write(f"Thread ID (TID): {proc.info['pid']}\n")
            file.write(f"Start Time: {proc.info['create_time']}\n")
            file.write(f"End Time: {psutil.Process(proc.info['pid']).status()}\n")
            file.write(f"Parent Process ID (PPID): {proc.info['ppid']}\n")
            file.write(f"Status: {proc.info['status']}\n")
            file.write("\n")

    # Extract and save network connections
    with open(network_connections_path, 'w') as file:
        for conn in psutil.net_connections():
            if conn.laddr and conn.raddr:  # Check if IP addresses are valid
                file.write(f"Source IP: {conn.laddr.ip}\n")
                file.write(f"Destination IP: {conn.raddr.ip}\n")
                file.write(f"Local Port: {conn.laddr.port}\n")
                file.write(f"Remote Port: {conn.raddr.port}\n")
                file.write(f"Protocol: {conn.type}\n")
                file.write(f"Status: {conn.status}\n")
                file.write("\n")

    # Extract and save file system metadata
    with open(file_system_metadata_path, 'w') as file:
        for partition in psutil.disk_partitions():
            file.write(f"Device: {partition.device}\n")
            file.write(f"Mount Point: {partition.mountpoint}\n")
            file.write(f"File System Type: {partition.fstype}\n")
            file.write(f"Options: {partition.opts}\n")
            file.write("\n")
            
            for entry in os.scandir(partition.mountpoint):
                file.write(f"Name: {entry.name}\n")
                file.write(f"Creation Time: {os.path.getctime(entry.path)}\n")
                file.write(f"Modification Time: {os.path.getmtime(entry.path)}\n")
                file.write(f"Attributes: {entry.stat().st_file_attributes}\n")
                file.write(f"Owner: {entry.stat().st_uid}\n")
                file.write(f"Access Permission: {entry.stat().st_mode}\n")
                file.write("\n")

    # Extract and save memory usage
    with open(memory_usage_path, 'w') as file:
        mem_info = psutil.Process().memory_info()
        file.write(f"Memory Allocation: {mem_info.rss}\n")
        file.write(f"Memory Deallocation: {mem_info.vms - mem_info.rss}\n")
        file.write("\n")
        for map_entry in psutil.Process().memory_maps(grouped=True):
            file.write(f"Path: {map_entry.path}\n")
            file.write(f"Size: {map_entry.rss}\n")
            file.write("\n")

    print("Kernel statistics extraction completed.")
except Exception as e:
    print("An error occurred during kernel statistics extraction:", str(e))

# Wait for user input before exiting
input("Press any key to exit...")
