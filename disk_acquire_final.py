import hashlib
import os
import sys
import ctypes
import wmi
import platform


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



def get_physical_drives_info():
    drives_info = []

    try:
        c = wmi.WMI()
        for drive in c.Win32_DiskDrive():
            total_size_bytes = int(drive.Size)
            total_size_mb = total_size_bytes / (1024 ** 2)
            drive_info = {
                'name': drive.DeviceID,
                'path': drive.DeviceID,
                'total_size_mb': total_size_mb,
                'total_size_bytes': total_size_bytes
            }
            drives_info.append(drive_info)
    except Exception as e:
        print(f"Error while getting drive info: {e}")

    return drives_info

def calculate_sha1(file_path, file_size):
    sha1_hash = hashlib.sha1()
    #file_size = 15825438720
    buffer_size = 1024 * 1024   # 1 MB buffer (1MB buffer)
    bytes_read = 0
    with open(file_path, "rb") as file:
        while bytes_read < file_size:
            remaining_bytes = min(file_size - bytes_read, buffer_size)
            data = file.read(remaining_bytes)
            if not data:
                break
            sha1_hash.update(data)
            bytes_read += len(data)
            mbs_read = bytes_read / (1024 * 1024 )
            print(f"MBs read: {mbs_read:.2f} MB  ", end="\r")
    print()  # Move to the next line after the progress is completed
    return sha1_hash.hexdigest()

def read_mbr(source_disk):
    mbr_data = None
    with open(source_disk, "rb") as disk:
        mbr_data = disk.read(512)  # Read the first 512 bytes (MBR)
    return mbr_data

def parse_partitions(mbr_data):
    partitions = []
    # Parse the MBR data to identify partitions (e.g., using the partition table entries)
    # Store the partition information in the 'partitions' list
    # Each partition entry should contain the start offset and size of the partition

    return partitions

def bit_to_bit_copy_with_hash(source_disk, destination_directory, disk_size):
    try:
        # Read the MBR to identify partitions
        mbr_data = read_mbr(source_disk)
        partitions = parse_partitions(mbr_data)

        # If no partitions are found, perform a bit-to-bit copy of the entire disk
        if not partitions:
            print("No partitions found on the disk. Performing a bit-to-bit copy of the entire disk.")
            #disk_size = get_disk_size(source_disk)
            #disk_size = 15825438720
            print ("The size in Bytes of the disk whose data is going to be extracted: ")
            print(disk_size)
            # Calculate SHA1 hash of the entire disk before acquisition
            sha1_disk_before = calculate_sha1(source_disk,disk_size)

            # Print the SHA1 hash of the entire disk before acquisition
            print("SHA1 hash of the entire disk before acquisition:")
            print(sha1_disk_before)

            # Open source disk in binary mode
            with open(source_disk, "rb") as source_handle:
                # Create disk image file
                disk_image_file = os.path.join(destination_directory, "entire_disk.dd")
                with open(disk_image_file, "wb") as disk_handle:
                    #sector_size = 512  # Size of each disk sector
                    buffer_size = 1024 * 1024  # 1 MB buffer

                    bytes_copied = 0
                    print("Copying... (This might take a while)")
                    while bytes_copied < int(disk_size):
                        buffer = source_handle.read(buffer_size)
                        disk_handle.write(buffer)

                        bytes_copied += len(buffer)
                        mbs_copied = bytes_copied / (1024 * 1024)
                        print(f"MBs copied: {mbs_copied:.2f} MB  ", end="\r")

                   
            print("\n The disk copy is acquired and saved in the current directory")
            print()  # Move to the next line after the copy is completed

            # Get the final SHA1 hash of the entire disk after acquisition
            
            sha1_disk_copied = calculate_sha1(disk_image_file,disk_size)
            print("SHA1 hash of the entire_disk.dd")
            print(sha1_disk_copied)
            # Print the SHA1 hash of the entire disk after acquisition
            sha1_disk_after = calculate_sha1(source_disk,disk_size)
            print("SHA1 hash of the entire disk after acquisition:")
            print(sha1_disk_after)

            
            
        else:
            # Partitions are found, perform bit-to-bit copy with hash for each partition
            for i, partition_info in enumerate(partitions):
                partition_start = partition_info['start']
                partition_size = partition_info['size']

                # Calculate SHA1 hash of the partition before acquisition
                sha1_partition_before = calculate_sha1(source_disk,partition_size)

                # Print the SHA1 hash of the partition before acquisition
                print(f"Partition {i + 1}: SHA1 hash before acquisition:")
                print(sha1_partition_before)

                # Open source disk in binary mode
                with open(source_disk, "rb") as source_handle:
                    source_handle.seek(partition_start)  # Move to the partition's start position

                    # Create partition image file
                    partition_image_file = os.path.join(destination_directory, f"partition_{i + 1}.dd")
                    with open(partition_image_file, "wb") as partition_handle:
                        buffer_size = 1024 * 1024  # 1 MB buffer
                        bytes_copied = 0

                        while bytes_copied < partition_size:
                            remaining_bytes = min(partition_size - bytes_copied, buffer_size)
                            data = source_handle.read(remaining_bytes)
                            if not data:
                                break

                            # Write data to the partition image file
                            partition_handle.write(data)

                            # Update SHA1 hash
                            sha1_partition_before.update(data)

                            bytes_copied += len(data)

                            # Print progress
                            mbs_copied = bytes_copied / (1024 * 1024)
                            print(f"Partition {i + 1}: MBs copied: {mbs_copied:.2f} MB  ", end="\r")

                print()  # Move to the next line after the copy is completed

                # Get the final SHA1 hash of the partition after acquisition
                sha1_partition_after = calculate_sha1(source_disk, disk_size)

                # Print the SHA1 hash of the partition after acquisition
                print(f"Partition {i + 1}: SHA1 hash after acquisition:")
                print(sha1_partition_after)

    except Exception as e:
        print("\nAn error occurred during the copy process:", e)


if __name__ == "__main__":
    #list_available_disks()
    # Restart the script with admin privileges
    restart_with_admin()
    i=1
    physical_drives_info = get_physical_drives_info()
    #print(physical_drives_info)
    if physical_drives_info:
        print("Physical Drives Information:")
        for drive_info in physical_drives_info:
            print(i)
            print("\n")
            print(f"Name: {drive_info['name']}")
            print(f"Path: {drive_info['path']}")
            print(f"Total Size (MB): {drive_info['total_size_mb']:.2f} MB")
            print(f"Total Size (Bytes): {drive_info['total_size_bytes']} Bytes")
            print("------------------------")
            i=i+1
    else:
        print("No physical drives found.")

    choice = int(input("Enter the disk you want to work with   "))
    choiced_disk = physical_drives_info[choice-1]
    source_disk = choiced_disk['path']
    disk_size_in_Bytes = int(choiced_disk['total_size_bytes'])
    destination_directory = os.getcwd()
    """
    # Check if the script is running with administrator privileges
    if not ctypes.windll.shell32.IsUserAnAdmin():
        # Re-run the script with administrator privileges
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        sys.exit()
    """
    bit_to_bit_copy_with_hash(source_disk, destination_directory,disk_size_in_Bytes)
    input("Enter any key to continue...")