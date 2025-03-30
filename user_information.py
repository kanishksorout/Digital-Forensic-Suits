import os
import psutil
import platform
import win32net
import datetime

def get_system_info():
    system_info = {}
    system_info['Name'] = platform.node()
    system_info['DNS Host Name'] = platform.node()
    system_info['Domain'] = platform.node().split('.')[1] if '.' in platform.node() else ''
    system_info['System'] = platform.uname().system
    system_info['Primary Owner Name'] = os.environ.get('USERNAME')
    system_info['Total Physical Memory'] = psutil.virtual_memory().total
    system_info['Workgroup'] = platform.node().split('.')[1] if '.' in platform.node() else ''
    return system_info

def get_user_sessions():
    return psutil.users()

def get_user_profiles():
    user_profiles = []
    users = win32net.NetUserEnum(None, 0)
    for user in users[0]:
        user_info = win32net.NetUserGetInfo(None, user['name'], 2)
        user_profile = {}
        user_profile['User Name'] = user['name']
        user_profile['Local Path'] = user_info['home_dir']
        #user_profile['SID'] = user_info['user_sid']
        user_profile['password'] = user_info['password']
        user_profile['password age'] = user_info['password_age']
        user_profile['script path'] = user_info['script_path']
        user_profile['comment'] = user_info['comment']
        user_profile['Full Name'] = user_info['full_name']
        user_profile['Last Used'] = datetime.datetime.fromtimestamp(user_info['last_logon']).strftime('%Y-%m-%d %H:%M:%S')
        user_profiles.append(user_profile)
    return user_profiles

def get_administrator_accounts():
    admins = win32net.NetLocalGroupGetMembers(None, 'Administrators', 2)
    return [admin['domainandname'] for admin in admins[0]]

def get_local_groups():
    groups = win32net.NetLocalGroupEnum(None, 0)
    return groups[0]

def save_user_info(filename):
    with open(filename, 'w') as file:
        system_info = get_system_info()
        file.write("System Details:\n")
        for key, value in system_info.items():
            file.write(f"{key}: {value}\n")

        file.write("\nLogon Sessions:\n")
        for session in get_user_sessions():
            file.write(f"User: {session.name}\nTerminal: {session.terminal}\nHost: {session.host}\n")

        file.write("\nUser Profiles:\n")
        for profile in get_user_profiles():
            file.write(f"User Name: {profile['User Name']}\n Local Path: {profile['Local Path']}\n Password: {profile['password']}\n password age: {profile['password age']}\n script path: {profile['script path']}\n comment: {profile['comment']}\n Full Name: {profile['Full Name']}\n Last Used: {profile['Last Used']}\n\n")

        file.write("\nAdministrator Accounts:\n")
        for admin in get_administrator_accounts():
            file.write(f"{admin}\n")

        file.write("\nLocal Groups:\n")
        for group in get_local_groups():
            file.write(f"Name: {group['name']}\n")

if __name__ == "__main__":
    save_user_info("user_info.txt")
