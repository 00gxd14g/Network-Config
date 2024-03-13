import subprocess
import re
from tabulate import tabulate
from termcolor import colored

def run_command(command):
    """
    Executes the given command and returns its output.
    If there's an error, returns the error instead.
    """
    try:
        return subprocess.check_output(command, shell=True).decode('utf-8')
    except subprocess.CalledProcessError as e:
        return str(e)

def get_network_interfaces():
    """
    Fetches and returns a list of network interfaces using the 'ip link show' command.
    """
    interfaces_output = run_command('ip link show')
    interfaces = re.findall(r'\d+: ([^:]+):', interfaces_output)
    return interfaces

def get_ip_addresses():
    """
    Fetches and returns a list of IP addresses assigned to network interfaces.
    Uses the 'ip addr' command and extracts the interface names and their corresponding IP addresses.
    """
    ip_output = run_command('ip addr')
    ips = re.findall(r'\d+: ([^:]+):.*?inet (\S+)', ip_output, re.DOTALL)
    return ips

def get_dns_settings():
    """
    Fetches and returns the current DNS settings using the 'systemd-resolve --status' command.
    In case of an error (e.g., command not found), returns the error message.
    """
    try:
        dns_output = run_command('systemd-resolve --status')
        return dns_output
    except Exception as e:
        return str(e)

def display_data(data, headers):
    """
    Displays the given data in a table format using the tabulate library.
    Accepts data as a list of tuples and headers as a list of strings.
    """
    print(tabulate(data, headers=headers, tablefmt="grid"))

def configure_network():
    """
    Provides an interface for configuring network settings such as IP address and gateway.
    Asks the user for the interface, new IP address, and default gateway, then applies these settings.
    """
    print(colored("\nConfiguration Options:", 'yellow'))
    interface = input(colored("Enter the name of the interface you want to configure: ", 'green'))
    new_ip = input(colored("Enter the new IP address (e.g., 192.168.1.10/24): ", 'green'))
    gateway = input(colored("Enter the default gateway (e.g., 192.168.1.1): ", 'green'))

    ip_cmd = f"sudo ip addr add {new_ip} dev {interface}"
    gw_cmd = f"sudo ip route add default via {gateway}"

    print(colored("\nApplying configuration...", 'blue'))
    print(run_command(ip_cmd))
    print(run_command(gw_cmd))
    print(colored("Configuration completed.", 'green'))

def main():
    """
    Main function to execute the script.
    Displays current network interfaces, IP addresses, and DNS settings.
    Then asks the user if they want to change the configuration, and proceeds accordingly.
    """
    print(colored("Current Network Interfaces:", 'blue'))
    interfaces = get_network_interfaces()
    display_data([(i, intf) for i, intf in enumerate(interfaces, 1)], ["Index", "Interface"])

    print(colored("\nCurrent IP Addresses:", 'blue'))
    ip_addresses = get_ip_addresses()
    display_data(ip_addresses, ["Interface", "IP Address"])

    print(colored("\nCurrent DNS Settings:", 'blue'))
    dns_settings = get_dns_settings()
    print(dns_settings)

    change_config = input(colored("\nDo you want to change the configuration? (yes/no): ", 'green')).strip().lower()
    if change_config == 'yes':
        configure_network()

if __name__ == "__main__":
    main()
