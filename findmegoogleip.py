#! /usr/bin/python3.4

import random
import urllib.request
import json
import subprocess
import threading
import sys
import pprint
import time
import socket
import ssl
import html.parser
import re


class FindMeGoogleIP:
    def __init__(self, locations):
        self.locations = locations
        self.dns_servers = []
        self.resolved_ips = {}
        self.ip_with_time = []
        self.available_ips = []
        self.reachable = []

    @staticmethod
    def read_domains():
        url = 'http://public-dns.tk/'
        print('retrieving domain list from %s' % url)
        try:
            data = urllib.request.urlopen(url).read().decode()
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

    def get_dns_servers(self):
        """Get the public dns server list from public-dns.tk"""
        if self.locations == ['all']:
            self.locations = FindMeGoogleIP.read_domains()
        urls = ['http://public-dns.tk/nameserver/%s.json' % location for location in self.locations]

        threads = []
        for url in urls:
            threads.append(GetDnsServer(url, self.dns_servers))

        FindMeGoogleIP.run_threads(threads, 20)

    def lookup_ips(self):
        threads = []
        for server in self.dns_servers:
            threads.append(NsLookup('google.com', server, self.resolved_ips))
            # threads.append(NsLookup('googlevideo.com', server, self.resolved_ips))

        FindMeGoogleIP.run_threads(threads)

    def ping(self):
        ping_results = {}
        threads = []
        for ip in self.resolved_ips:
            threads.append(Ping(ip, ping_results))

        FindMeGoogleIP.run_threads(threads)

        for k, v in ping_results.items():
            if v['loss'] == 0:
                self.ip_with_time.append((k, v['time']))

        self.ip_with_time = sorted(self.ip_with_time, key=lambda x: x[1])
        self.available_ips = [x[0] for x in self.ip_with_time]

    def check_service(self):
        threads = []
        for ip in self.available_ips:
            threads.append(ServiceCheck(ip, self.resolved_ips[ip], self.reachable))

        FindMeGoogleIP.run_threads(threads)

    def cleanup_low_quality_ips(self):
        """
        For ips in the same range, if success_rate does not satisfy a pre-defined threshold,
        they'll be all treated as low quality and removed.
        """
        reachable = set(self.reachable)
        success_count = {}
        fail_count = {}
        success_rate = {}
        threshold = 80  # 80%

        for ip in self.available_ips:
            prefix = self.get_ip_prefix(ip)
            if ip in reachable:
                success_count[prefix] = success_count.get(prefix, 0) + 1
            else:
                fail_count[prefix] = fail_count.get(prefix, 0) + 1

        for prefix in success_count.keys():
            success_rate[prefix] = 100 * success_count[prefix] // (success_count[prefix] + fail_count.get(prefix, 0))

        self.reachable = [ip for ip in self.reachable if success_rate[self.get_ip_prefix(ip)] >= threshold]

    @staticmethod
    def get_ip_prefix(ip):
        return re.sub('\.[0-9]+$', '', ip)

    def show_results(self):
        if self.reachable:
            reachable_ip_with_time = [(ip, rtt) for (ip, rtt) in self.ip_with_time if ip in self.reachable]

            print("%d IPs ordered by delay time:" % len(reachable_ip_with_time))
            pprint.PrettyPrinter().pprint(reachable_ip_with_time)

            fast_ips = []
            slow_ips = []
            for ip, rtt in reachable_ip_with_time:
                if rtt <= 200:
                    fast_ips.append(ip)
                else:
                    slow_ips.append(ip)
            print("%d IPs concatenated:" % len(self.reachable))
            if fast_ips:
                FindMeGoogleIP.highlight_print('|'.join(fast_ips))
            if slow_ips:
                if fast_ips:
                    print('|', end="")
                print('|'.join(slow_ips))
            else:
                print()
        else:
            print("No available servers found")

    @staticmethod
    def highlight_print(word):
        green = '\033[32m'
        reset = '\033[0m'
        print(green + word + reset, end="")

    def run(self):
        self.get_dns_servers()
        self.lookup_ips()
        self.ping()
        self.check_service()
        self.cleanup_low_quality_ips()
        self.show_results()


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
            socket.setdefaulttimeout(2)
            conn = ssl.create_default_context().wrap_socket(socket.socket(), server_hostname=self.host)
            conn.connect((self.ip, self.port))
            self.lock.acquire()
            self.servicing.append(self.ip)
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
            data = urllib.request.urlopen(self.url).read().decode()
            servers = json.loads(data)
            self.lock.acquire()
            for server in servers:
                if '.' in server['ip']:
                    self.dns_servers.append(server['ip'])
            self.lock.release()
        except IOError:
            print("Cannot get data from %s" % self.url)


class NsLookup(threading.Thread):
    def __init__(self, name, server, store):
        threading.Thread.__init__(self)
        self.name = name
        self.server = server
        self.lock = None
        self.store = store

    def run(self):
        try:
            print('looking up %s from %s' % (self.name, self.server))
            output = subprocess.check_output(["nslookup", self.name, self.server])
            ips = self.parse_nslookup_result(output.decode())
            self.lock.acquire()
            for ip in ips:
                if not self.is_spf(ip):
                    self.store[ip] = self.name
            self.lock.release()
        except subprocess.CalledProcessError:
            pass

    @staticmethod
    def is_spf(ip):
        ips = {'64.18.', '64.233.', '66.102.', '66.249.', '72.14.', '74.125.', '173.194.', '207.126.', '209.85.',
               '216.58.', '216.239.'}
        if re.sub('\.[0-9]+\.[0-9]+$', '.', ip) in ips:
            return True
        else:
            return False

    @staticmethod
    def parse_nslookup_result(result):
        """Parse the result of nslookup and return a list of ip"""
        ips = []
        lines = result.split('\n')
        del lines[0]
        del lines[1]
        for line in lines:
            if line.startswith('Address: '):
                ips.append(line.replace('Address: ', ''))
        return ips


class Ping(threading.Thread):
    def __init__(self, server, store):
        threading.Thread.__init__(self)
        self.server = server
        self.lock = None
        self.store = store

    def run(self):
        try:
            print('pinging %s' % (self.server,))
            output = subprocess.check_output(["ping", '-c 5', '-q', self.server])
            self.lock.acquire()
            self.store[self.server] = self.parse_ping_result(output.decode())
            self.lock.release()
        except subprocess.CalledProcessError:
            pass

    @staticmethod
    def parse_ping_result(result):
        loss = result.split('\n')[-3].split(', ')[2].split(' ')[0].replace('%', '')
        trip_time = result.split('\n')[-2].split(' = ')[-1].split('/')[1]
        return {'loss': float(loss), 'time': float(trip_time)}


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


if len(sys.argv) >= 2:
    FindMeGoogleIP(sys.argv[1:]).run()
else:
    print("Usage:")
    print("Find ips in specified domains: findmegoogleip.py kr us")
    print("=" * 50)
    print("Now running default: find ip from a randomly chosen domain")
    FindMeGoogleIP([random.choice(FindMeGoogleIP.read_domains())]).run()
