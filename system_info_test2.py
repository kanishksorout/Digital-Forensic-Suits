# -*- coding: utf-8 -*-
"""

@author: PRIME
"""

import os
import platform
import subprocess
import wmi
import winreg
import datetime
from tabulate import tabulate

def get_installed_programs():
    cmd = 'wmic product get name, version, vendor, installdate, installsource, packagecode, localpackage'
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    return result.stdout

def get_installed_programs_from_registry():
    programs = []
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as key:
        for i in range(winreg.QueryInfoKey(key)[0]):
            subkey_name = winreg.EnumKey(key, i)
            with winreg.OpenKey(key, subkey_name) as subkey:
                try:
                    name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                    version = winreg.QueryValueEx(subkey, "DisplayVersion")[0]
                    publisher = winreg.QueryValueEx(subkey, "Publisher")[0]
                    install_date = winreg.QueryValueEx(subkey, "InstallDate")[0]
                    programs.append([name, version, publisher, install_date])
                except FileNotFoundError:
                    pass
    return programs

def get_environment_variables():
    env_vars = os.environ
    return [[key, value] for key, value in env_vars.items()]

def get_system_information():
    wmi_obj = wmi.WMI()
    system = wmi_obj.Win32_ComputerSystem()[0]
    os_info = wmi_obj.Win32_OperatingSystem()[0]

    system_info_data = [
        ['Name', system.Name],
        ['Caption', system.Caption],
        ['System Type', system.SystemType],
        ['Manufacturer', system.Manufacturer],
        ['Model', system.Model],
        ['DNS Host Name', system.DNSHostName],
        ['Domain', system.Domain],
        ['Domain Role', system.DomainRole],
        ['Workgroup', system.Workgroup],
        ['Current Time Zone', system.CurrentTimeZone],
        ['PC System Type', system.PCSystemType],
        ['Hypervisor Present', system.HypervisorPresent],
        ['OS Name', os_info.Name],
        ['Description', os_info.Description],
        ['Version', os_info.Version],
        ['Build Number', os_info.BuildNumber],
        ['Install Date', os_info.InstallDate],
        ['System Drive', os_info.SystemDrive],
        ['System Device', os_info.SystemDevice],
        ['Windows Directory', os_info.WindowsDirectory],
        ['Last Bootup Time', os_info.LastBootUpTime],
        ['Locale', os_info.LocalDateTime]
    ]
    return system_info_data

def get_hotfixes():
    cmd = 'wmic qfe get HotFixID, InstalledOn'
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    hotfix_data = [line.strip().split() for line in result.stdout.splitlines() if line.strip()]
    return hotfix_data

def get_window_defender_status():
    cmd = 'powershell Get-MpComputerStatus | Select-Object AMProductVersion, AntispywareSignatureAge, EngineVersion, AntivirusSignatureAge'
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    defender_data = [line.strip().split(": ") for line in result.stdout.splitlines() if line.strip()]
    return defender_data

# Extracting information
installed_programs = get_installed_programs_from_registry()
env_variables = get_environment_variables()
system_info = get_system_information()
hotfixes = get_hotfixes()
window_defender_status = get_window_defender_status()

# Saving the information to the file
with open("system_information.txt", "w", encoding="utf-8") as file:
    file.write("Installed Programs:\n")
    file.write(tabulate(installed_programs, headers=["Name", "Version", "Publisher", "Install Date"], tablefmt="grid") + "\n\n")
    file.write("Environment Variables:\n")
    file.write(tabulate(env_variables, headers=["Name", "Value"], tablefmt="grid") + "\n\n")
    file.write("System Information:\n")
    file.write(tabulate(system_info, headers=["Property", "Value"], tablefmt="grid") + "\n\n")
    file.write("Hotfixes:\n")
    file.write(tabulate(hotfixes, headers=["HotFixID", "InstalledOn"], tablefmt="grid") + "\n\n")
    file.write("Window Defender Status:\n")
    file.write(tabulate(window_defender_status, headers=["Property", "Value"], tablefmt="grid") + "\n\n")

print("System information has been saved to 'system_information.txt'")
