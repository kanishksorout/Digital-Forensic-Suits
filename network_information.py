import psutil
import subprocess
import socket
import os
from tabulate import tabulate

def get_network_adapter_info():
    adapters_info = []

    for interface, addresses in psutil.net_if_addrs().items():
        for address in addresses:
            if address.family == psutil.AF_LINK:
                adapter_info = [
                    interface,
                    address.address,
                    psutil.net_if_stats()[interface].isup,
                    psutil.net_if_stats()[interface].duplex,
                    psutil.net_if_stats()[interface].speed,
                    psutil.net_if_stats()[interface].mtu
                ]
                adapters_info.append(adapter_info)

    return adapters_info

def get_current_ip_configuration():
    ip_configs = []

    for interface, addresses in psutil.net_if_addrs().items():
        for address in addresses:
            ip_config = [
                interface,
                address.address,
                address.netmask,
                address.broadcast,
                address.ptp,
                address.family
            ]
            ip_configs.append(ip_config)

    return ip_configs


def get_network_adapter_ips():
    adapter_ips = []

    for interface, data in psutil.net_if_stats().items():
        if data.isup:
            addresses = psutil.net_if_addrs().get(interface, [])
            for address in addresses:
                if address.family == socket.AF_INET or address.family == socket.AF_INET6:
                    adapter_ip = [
                        interface,
                        address.address,
                        data.isup,
                        data.duplex,  # Using duplex instead of status
                        data.speed    # Using speed instead of status
                    ]
                    adapter_ips.append(adapter_ip)

    return adapter_ips


def get_current_connection_profiles():
    connection_profiles = []

    for connection in psutil.net_connections(kind='inet'):
        profile = [
            connection.pid,
            connection.fd,
            connection.family,
            connection.type,
            connection.laddr.ip,
            connection.laddr.port,
            connection.raddr.ip if connection.raddr else '',  # Access the IP address from the tuple
            connection.raddr.port if connection.raddr else '',  # Access the port number from the tuple
            connection.status
        ]
        connection_profiles.append(profile)

    return connection_profiles


def get_wifi_networks():
    wifi_profiles = []

    try:
        output = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles']).decode('utf-8').split('\n')
        profile_names = [line.split(':')[1].strip() for line in output if "All User Profile" in line]

        for profile in profile_names:
            try:
                output = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', profile, 'key=clear']).decode('utf-8')
                password_line = [line.strip() for line in output.split('\n') if "Key Content" in line]
                if password_line:
                    password = password_line[0].split(':')[1].strip()
                else:
                    password = "Password not available"
                wifi_profiles.append([profile, password])
            except subprocess.CalledProcessError:
                pass
    except subprocess.CalledProcessError:
        pass

    return wifi_profiles

def get_arp_cache():
    arp_cache = []

    try:
        output = subprocess.check_output(['arp', '-a']).decode('utf-8').split('\n')
        for line in output[3:-1]:
            parts = line.split()
            if len(parts) == 3:
                arp_entry = [
                    parts[1],
                    parts[0],
                    parts[2]
                ]
                arp_cache.append(arp_entry)
    except subprocess.CalledProcessError:
        pass

    return arp_cache

def get_current_tcp_connections():
    tcp_connections = []

    for connection in psutil.net_connections(kind='inet'):
        profile = [
            connection.pid,
            connection.fd,
            connection.family,
            connection.type,
            connection.laddr.ip,
            connection.laddr.port,
            connection.raddr[0] if connection.raddr else '',  # Access the IP address from the tuple
            connection.raddr[1] if connection.raddr else '',  # Access the port number from the tuple
            connection.status
        ]
        tcp_connections.append(profile)

    return tcp_connections


def get_firewall_rules():
    firewall_rules = []

    try:
        output = subprocess.check_output(['netsh', 'advfirewall', 'firewall', 'show', 'rule', 'name=all']).decode('utf-8')
        lines = output.split('\n')
        rule_names = [line.strip() for line in lines if "Rule Name:" in line]

        for rule_name in rule_names:
            firewall_rules.append([rule_name])
    except subprocess.CalledProcessError:
        pass

    return firewall_rules

def save_to_file(data, filename):
    headers = {
        "network_adapter_info": ["Interface", "Address", "Is Up", "Duplex", "Speed", "MTU"],
        "current_ip_config": ["Interface", "Address", "Netmask", "Broadcast", "PTP", "Family"],
        "adapter_ips": ["Interface", "Address", "Is Up", "Duplex", "Speed"],
        "connection_profiles": ["PID", "FD", "Family", "Type", "Local Address", "Local Port", "Remote Address", "Remote Port", "Status"],
        "wifi_networks": ["Profile Name", "Password"],
        "arp_cache": ["Interface Alias", "IP Address Linkage", "Address"],
        "tcp_connections": ["Local Address", "Local Port", "Remote Address", "Remote Port", "Status", "Owning Process"],
        "firewall_rules": ["Rule Name"]
    }

    if isinstance(data, list) and data:
        table_name = filename.split(".")[0]  # Get table name from filename
        table_headers = headers.get(table_name, [])
        if table_headers:
            table = tabulate(data, headers=table_headers, tablefmt="grid", showindex=False)
            with open(filename, 'w') as file:
                file.write(table)
            print(f"{table_name} data saved to {filename}")
        else:
            print(f"Unknown table name: {table_name}")
    else:
        print(f"No data found for {filename}")


if __name__ == "__main__":
    os.getcwd()
    network_adapter_info = get_network_adapter_info()
    current_ip_config = get_current_ip_configuration()
    adapter_ips = get_network_adapter_ips()
    connection_profiles = get_current_connection_profiles()
    wifi_networks = get_wifi_networks()
    arp_cache = get_arp_cache()
    tcp_connections = get_current_tcp_connections()
    firewall_rules = get_firewall_rules()

    save_to_file(network_adapter_info, "network_adapter_info.txt")
    save_to_file(current_ip_config, "current_ip_config.txt")
    save_to_file(adapter_ips, "adapter_ips.txt")
    save_to_file(connection_profiles, "connection_profiles.txt")
    save_to_file(wifi_networks, "wifi_networks.txt")
    save_to_file(arp_cache, "arp_cache.txt")
    save_to_file(tcp_connections, "tcp_connections.txt")
    save_to_file(firewall_rules, "firewall_rules.txt")