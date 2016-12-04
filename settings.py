# the number of threads(dns query or ssl service check) running concurrently
threads = 100

# the maximum number of dns servers to query in a certain country
servers = 800

# the proxies to access public dns website
# proxies = None
proxies = {
    'http': 'http://127.0.0.1:8087',
    'https': 'http://127.0.0.1:8087',
}
