#! /usr/bin/python3.4

import random
import threading
import sys
import time
import socket
import ssl
import re
import dns.resolver
import dns.exception
import os
import urllib.request


class FindMeGoogleIP:
    DNS_SERVERS_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'dns_servers')

    def __init__(self, locations):
        self.locations = locations
        self.dns_servers = []
        self.resolved_ips = {}
        self.reachable = []

    @staticmethod
    def read_domains():
        return [file.replace('.txt', '') for file in os.listdir(FindMeGoogleIP.DNS_SERVERS_DIR)]

    @staticmethod
    def run_threads(threads, limit=200):
        """A general way to run multiple threads"""
        lock = threading.Lock()
        for thread in threads:
            thread.lock = lock
            if threading.active_count() > limit:
                time.sleep(1)

            thread.start()

        for thread in threads:
            thread.join()

    def get_dns_servers(self):
        if self.locations == ['all']:
            self.locations = self.read_domains()
        files = [os.path.join(self.DNS_SERVERS_DIR, location+'.txt') for location in self.locations]

        try:
            for file in files:
                print('read servers from file %s' % file)
                f = open(file)
                data = f.read().strip()
                if data:
                    servers = re.split('\s+', data)
                    random.shuffle(servers)
                    self.dns_servers.extend(servers[:200])  # take 200 servers for faster running
                f.close()
        except IOError:
            print("Cannot read dns servers")

    def lookup_ips(self):
        threads = []
        for server in self.dns_servers:
            threads.append(NsLookup('google.com', server, self.resolved_ips))

        FindMeGoogleIP.run_threads(threads)

    def check_service(self):
        threads = []
        for ip in self.resolved_ips.keys():
            threads.append(ServiceCheck(ip, self.resolved_ips[ip], self.reachable))

        FindMeGoogleIP.run_threads(threads)

    def cleanup_low_quality_ips(self):
        """
        For ips in the same range, if success_rate does not satisfy a pre-defined threshold,
        they'll be all treated as low quality and removed.
        """
        reachable = {ip for ip, rtt in self.reachable}
        success_count = {}
        fail_count = {}
        success_rate = {}
        threshold = 80  # 80%

        for ip in self.resolved_ips.keys():
            prefix = self.get_ip_prefix(ip)
            if ip in reachable:
                success_count[prefix] = success_count.get(prefix, 0) + 1
            else:
                fail_count[prefix] = fail_count.get(prefix, 0) + 1

        for prefix in success_count.keys():
            success_rate[prefix] = 100 * success_count[prefix] // (success_count[prefix] + fail_count.get(prefix, 0))

        self.reachable = [(ip, rtt) for ip, rtt in self.reachable
                          if success_rate.get(self.get_ip_prefix(ip), 0) >= threshold]

    @staticmethod
    def get_ip_prefix(ip):
        return re.sub('\.[0-9]+$', '', ip)

    def show_results(self):
        if self.reachable:
            reachable_sorted = sorted(self.reachable, key=lambda x: x[1])

            print("%d IPs ordered by approximate delay time(milliseconds):" % len(reachable_sorted))
            for item in reachable_sorted:
                print(item)

            print("%d IPs concatenated:" % len(self.reachable))
            print('|'.join([ip for ip, rtt in reachable_sorted]))
        else:
            print("No available servers found")

    def run(self):
        self.get_dns_servers()
        self.lookup_ips()
        self.check_service()
        self.cleanup_low_quality_ips()
        self.show_results()

    @staticmethod
    def update_dns_files():
        threads = []
        for location in FindMeGoogleIP.read_domains():
            threads.append(DNSServerFileDownload(location))
        FindMeGoogleIP.run_threads(threads, 100)
        print('finished')


class DNSServerFileDownload(threading.Thread):
    def __init__(self, location):
        threading.Thread.__init__(self)
        self.domain = location
        self.url = "http://public-dns.tk/nameserver/%s.txt" % location
        self.file = os.path.join(FindMeGoogleIP.DNS_SERVERS_DIR, '%s.txt' % location)
        self.lock = None

    def run(self):
        try:
            print('downloading file %s' % self.url)
            data = urllib.request.urlopen(self.url, timeout=5).read().decode()
            f = open(self.file, mode='w')
            f.write(data)
        except IOError as err:
            print('cannot(%s) update file %s' % (str(err), self.file))


class ServiceCheck(threading.Thread):
    def __init__(self, ip, host, servicing):
        threading.Thread.__init__(self)
        self.ip = ip
        self.host = host
        self.port = 443
        self.lock = None
        self.servicing = servicing

    def run(self):
        try:
            print('checking ssl service %s:%s' % (self.ip, self.port))
            socket.setdefaulttimeout(5)
            conn = ssl.create_default_context().wrap_socket(socket.socket(), server_hostname=self.host)
            conn.connect((self.ip, self.port))

            start = time.time()
            socket.create_connection((self.ip, self.port))
            end = time.time()
            rtt = int((end-start)*1000)  # milliseconds

            self.lock.acquire()
            self.servicing.append((self.ip, rtt))
            self.lock.release()
        except (ssl.CertificateError, ssl.SSLError, socket.timeout, ConnectionError) as err:
            print("error(%s) on connecting %s:%s" % (str(err), self.ip, self.port))


class NsLookup(threading.Thread):
    def __init__(self, name, server, store):
        threading.Thread.__init__(self)
        self.name = name
        self.server = server
        self.lock = None
        self.store = store
        self.resolver = dns.resolver.Resolver()
        self.resolver.nameservers = [server]
        self.resolver.lifetime = 5

    def run(self):
        try:
            print('looking up %s from %s' % (self.name, self.server))
            answer = self.resolver.query(self.name)
            self.lock.acquire()
            for response in answer:
                ip = str(response)
                if not self.is_spf(ip):
                    self.store[ip] = self.name
            self.lock.release()
        except dns.exception.DNSException:
            pass

    @staticmethod
    def is_spf(ip):
        ips = {'64.18.', '64.233.', '66.102.', '66.249.', '72.14.', '74.125.', '173.194.', '207.126.', '209.85.',
               '216.58.', '216.239.'}
        if re.sub('\.[0-9]+\.[0-9]+$', '.', ip) in ips:
            return True
        else:
            return False


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        FindMeGoogleIP(sys.argv[1:]).run()
    else:
        domain = [random.choice(FindMeGoogleIP.read_domains())]
        print("Usage:")
        print("Find ips in specified domains: findmegoogleip.py kr us")
        print("=" * 50)
        print("Now running default: find ip from a randomly chosen domain: %s" % domain[0])
        FindMeGoogleIP(domain).run()
