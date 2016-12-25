# the number of threads(dns query or ssl service check) running concurrently
threads = 100

# the maximum number of dns servers to query in a certain country
servers = 800

# Set the proxies to access public dns website if this variable is not None
# proxies = None
proxies = {
    'http': 'http://127.0.0.1:8087',
    'https': 'http://127.0.0.1:8087',
}

# Write the IPs into gae.user.json if this variable is not None
# gae_user_json_file = None
gae_user_json_file = r'C:\Projects\goproxy_windows_amd64\gae.user.json'
