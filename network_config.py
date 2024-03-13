import subprocess
import re
import yaml
import os
from tabulate import tabulate
from termcolor import colored

def run_command(command):
    """
    Executes the given command and returns its output.
    If there's an error, returns the error message.
    """
    try:
        return subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT).decode('utf-8')
    except subprocess.CalledProcessError as e:
        return e.output.decode('utf-8')

def get_network_interfaces():
    """
    Fetches and returns a list of network interfaces using the 'ip link show' command.
    """
    interfaces_output = run_command('ip link show')
    interfaces = re.findall(r'\d+: ([^:]+):', interfaces_output)
    return interfaces

def get_current_network_config(interface):
    """
    Uses the 'ip addr show' command to get the current IP configuration of the given interface.
    If the interface is using DHCP, it fetches the current IP address, gateway, and netmask.
    """
    ip_output = run_command(f'ip addr show {interface}')
    cidr = re.search(r'inet (\S+)', ip_output)
    gateway_output = run_command('ip route')
    gateway = re.search(r'default via (\S+)', gateway_output)
    return {
        'cidr': cidr.group(1) if cidr else 'Not set/Using DHCP',
        'gateway': gateway.group(1) if gateway else 'Not detected'
    }

def configure_network(interface, new_ip, gateway, dns_servers):
    """
    Configures the network settings for the given interface using Netplan.
    Sets a static IP address, gateway, and DNS servers.
    """
    config_path = f'/etc/netplan/01-netcfg-{interface}.yaml'
    config = {
        'network': {
            'version': 2,
            'renderer': 'networkd',
            'ethernets': {
                interface: {
                    'dhcp4': False,
                    'addresses': [new_ip],
                    'gateway4': gateway,
                    'nameservers': {
                        'addresses': dns_servers.split(',')
                    }
                }
            }
        }
    }
    
    with open(config_path, 'w') as file:
        yaml.dump(config, file)
    
    print(colored("\nApplying configuration with Netplan...", 'blue'))
    apply_result = run_command('sudo netplan apply')
    print(apply_result if apply_result else colored("Configuration applied successfully.", 'green'))

def main():
    print(colored("Current Network Interfaces:", 'blue'))
    interfaces = get_network_interfaces()
    display_data = [(i, intf) for i, intf in enumerate(interfaces, 1)]
    print(tabulate(display_data, headers=["Index", "Interface"], tablefmt="grid"))

    selected_index = int(input(colored("\nEnter the index of the interface you want to configure: ", 'green'))) - 1
    selected_interface = interfaces[selected_index]

    current_config = get_current_network_config(selected_interface)
    print(colored(f"\nCurrent configuration for {selected_interface}:", 'blue'))
    print(f"IP Address/Netmask: {current_config['cidr']}")
    print(f"Gateway: {current_config['gateway']}")

    new_ip = input(colored("\nEnter the new IP address with CIDR notation (e.g., 192.168.1.10/24): ", 'green'))
    gateway = input(colored("Enter the default gateway (e.g., 192.168.1.1): ", 'green'))
    dns_servers = input(colored("Enter DNS servers separated by comma (e.g., 8.8.8.8,8.8.4.4): ", 'green'))

    configure_network(selected_interface, new_ip, gateway, dns_servers)

if __name__ == "__main__":
    main()
