import re
import requests


def get_device_info(user_agent):
    # Example user agent string
    ua_string = user_agent

    # Define regex patterns for different devices/browsers
    device_patterns = {
        'Android': r'Android\s+([\d\.]+)',
        'iPhone': r'iPhone',
        'iPad': r'iPad',
        'Windows': r'Windows NT\s+([\d\.]+)',
        'Mac': r'Macintosh',
        'Linux': r'Linux'
    }

    for device, pattern in device_patterns.items():
        if re.search(pattern, ua_string):
            return device  # Return the device type

    return 'Unknown Device'  # If no match found

def is_private_ip(ip_address):
    if ip_address.startswith("10.") or ip_address.startswith("172."):
        return True
    if ip_address.startswith("192.168."):
        return True
    if ip_address == "127.0.0.1":
        return True
    return False

def get_location(ip_address):
    if is_private_ip(ip_address):
        print(f"Skipping location fetch for private IP: {ip_address}")
        return {
            'ip': ip_address,
            'city': 'Local Network',
            'region': 'Local Network',
            'country': 'Local Network',
            'latitude': 'N/A',
            'longitude': 'N/A'
        }

    try:
        response = requests.get(f'https://ipinfo.io/{ip_address}/json')
        data = response.json()

        if 'loc' in data:
            location_info = {
                'ip': data.get('ip'),
                'city': data.get('city'),
                'region': data.get('region'),
                'country': data.get('country'),
                'latitude': data['loc'].split(',')[0],
                'longitude': data['loc'].split(',')[1],
            }
        else:
            print("Location data not found in the response.")
            return None

        return location_info
    except Exception as e:
        print(f"Error fetching location: {e}")
        return None
