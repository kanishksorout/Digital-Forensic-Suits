#Author:@Prime (Kanishk sorout)
#Date : 30-03-2025
#This code is able to extract the PIDs list of all the process running in the system.
#The code will be create the file names as pid_list.txt that will contain all the processes list.
#The code will be able to create all the dmp files in the same directory inluding specific process name.
#The directory can be changed to desired directory in variable "dump_file_path" at line 61.

import psutil
import ctypes
import os

def acquire_memory_dump(pid, dump_file_path):
    if pid == 0:
        return None

    process_handle = None
    dump_file_handle = None

    try:
        # Open the target process with required access rights
        process_handle = ctypes.windll.kernel32.OpenProcess(
            0x1F0FFF,  # PROCESS_ALL_ACCESS
            False,
            pid
        )

        # Create the memory dump using MiniDumpWriteDump
        dump_file_handle = ctypes.windll.kernel32.CreateFileW(
            dump_file_path,
            0x10000000,  # GENERIC_WRITE
            0,
            None,
            2,  # CREATE_ALWAYS
            0,
            None
        )

        ctypes.windll.dbghelp.MiniDumpWriteDump(
            process_handle,
            pid,
            dump_file_handle,
            2,  # MiniDumpWithFullMemory
            None,
            None,
            None
        )

        return 100  # Return 100 to indicate 100% progress

    except Exception as e:
        print(f"An error occurred during memory dump creation for PID {pid}. Error: {str(e)}")

    finally:
        if process_handle:
            ctypes.windll.kernel32.CloseHandle(process_handle)
            
        if dump_file_handle:
            ctypes.windll.kernel32.CloseHandle(dump_file_handle)

def run():
    dir = os.getcwd()
    dump_directory = os.path.join(dir, "dumps")

    # Create the "list_of_pid_s" directory if it doesn't exist
    os.makedirs(dump_directory, exist_ok=True)

    # Get the list of all running processes and their PIDs
    processes = []
    for proc in psutil.process_iter(['pid', 'name']):
        processes.append((proc.info['pid'], proc.info['name']))

    # Print the list of processes
    for pid, name in processes:
        print(f"PID: {pid}\tName: {name}")

    # Save the list of PIDs to a file in the "list_of_pid_s" directory
    pid_list_file = os.path.join(dump_directory, "pid_list.txt")
    with open(pid_list_file, "w") as file:
        for pid, name in processes:
            file.write(f"PID: {pid}\tName: {name}\n")

    # Use the list of processes with their PIDs for memory dump creation
    for pid, _ in processes:
        dump_file_path = os.path.join(dump_directory, f"dump_file_{pid}.dmp")
        print(f"Extracting memory for PID {pid}...")
        progress_percentage = acquire_memory_dump(pid, dump_file_path)
        if progress_percentage is not None:
            print(f"Extraction progress for PID {pid}: {progress_percentage}%")

run()
