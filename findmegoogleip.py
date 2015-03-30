#! /usr/bin/python3.4

import random
import urllib.request
import json
import threading
import sys
import time
import socket
import ssl
import html.parser
import re
import dns.resolver
import dns.exception


class FindMeGoogleIP:
    def __init__(self, locations):
        self.locations = locations
        self.dns_servers = []
        self.resolved_ips = {}
        self.reachable = []

    @staticmethod
    def read_domains():
        url = 'http://public-dns.tk/'
        print('retrieving domain list from %s' % url)
        try:
            data = urllib.request.urlopen(url, timeout=5).read().decode()
            dlp = DomainListParser()
            dlp.feed(data)
            dlp.domain_list.remove('cn')
            return dlp.domain_list
        except IOError:
            print("Cannot get domain list from %s" % url)
            exit(1)

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

    def get_dns_servers(self, source='json'):
        """Get the public dns server list from public-dns.tk"""
        if self.locations == ['all']:
            self.locations = FindMeGoogleIP.read_domains()
        urls = ['http://public-dns.tk/nameserver/%s.%s' % (location, source) for location in self.locations]

        threads = []
        for url in urls:
            threads.append(GetDnsServer(url, self.dns_servers))

        FindMeGoogleIP.run_threads(threads, 20)

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
        self.run_others()
        if not self.reachable:
            self.get_dns_servers(source='txt')
            self.run_others()
        self.show_results()

    def run_others(self):
        self.lookup_ips()
        self.check_service()
        self.cleanup_low_quality_ips()


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


class GetDnsServer(threading.Thread):
    def __init__(self, url, dns_servers):
        threading.Thread.__init__(self)
        self.url = url
        self.lock = None
        self.dns_servers = dns_servers

    def run(self):
        try:
            print('retrieving dns servers from %s' % self.url)
            data = urllib.request.urlopen(self.url, timeout=5).read().decode()
            self.lock.acquire()
            if self.url.endswith('.json'):
                self.load_json(data)
            elif self.url.endswith('.txt'):
                self.load_text(data)
            self.lock.release()
        except IOError:
            print("Cannot get data from %s" % self.url)

    def load_json(self, data):
        servers = json.loads(data)
        for server in servers:
            if '.' in server['ip']:
                self.dns_servers.append(server['ip'])

    def load_text(self, data):
        self.dns_servers.extend(re.split('\s+', data.strip()))


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


class DomainListParser(html.parser.HTMLParser):
    def __init__(self):
        html.parser.HTMLParser.__init__(self)
        self.domain_list = []
        self.pattern = re.compile('/nameserver/([a-z][a-z]).html')

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            m = self.pattern.match(attrs[0][1])
            if m:
                self.domain_list.append(m.group(1))

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        FindMeGoogleIP(sys.argv[1:]).run()
    else:
        print("Usage:")
        print("Find ips in specified domains: findmegoogleip.py kr us")
        print("=" * 50)
        print("Now running default: find ip from a randomly chosen domain")
        FindMeGoogleIP([random.choice(FindMeGoogleIP.read_domains())]).run()
