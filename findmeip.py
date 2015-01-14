#! /usr/bin/python3

import urllib.request
import json
import subprocess
import threading
import sys
import pprint
import time


class FindMeIP:
    def __init__(self, hostname, country):
        self.hostname = hostname
        self.country = country
        self.dns_servers = []
        self.resolved_ips = set()
        self.ping_results = {}
        self.ip_with_time = []
        self.available_ips = set()
        self.web_reachable = set()

    def get_dns_servers(self):
        """Get the public dns server list from public-dns.tk"""
        if self.country == 'all':
            with open('countries.txt') as f:
                countries = [line.strip() for line in f.readlines() if line]
                urls = ['http://public-dns.tk/nameserver/%s.json' % country for country in countries]
        else:
            urls = ['http://public-dns.tk/nameserver/%s.json' % self.country]

        lock = threading.Lock()
        threads = []
        for url in urls:
            t = GetDnsServer(url, lock, self.dns_servers)
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

    def lookup_ips(self):
        lock = threading.Lock()
        threads = []
        for server in self.dns_servers:
            if threading.active_count() > 200:
                time.sleep(1)
            t = NsLookup(self.hostname, server, lock, self.resolved_ips)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

    def ping(self):
        lock = threading.Lock()
        threads = []
        for ip in self.resolved_ips:
            if threading.active_count() > 200:
                time.sleep(1)
            t = Ping(ip, lock, self.ping_results)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

    def check_web_reachable(self):
        lock = threading.Lock()
        threads = []
        for ip in self.available_ips:
            if threading.active_count() > 50:
                time.sleep(1)
            t = WebRequest(ip, lock, self.web_reachable)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

    def summarize(self):
        for k, v in self.ping_results.items():
            if v['loss'] == 0:
                self.ip_with_time.append((k, v['time']))

        self.ip_with_time = sorted(self.ip_with_time, key=lambda x: x[1])
        self.available_ips = [x[0] for x in self.ip_with_time]

    def show_results(self):
        if self.ip_with_time:
            print("IPs ordered by delay time:")
            pprint.PrettyPrinter().pprint(self.ip_with_time)
            print("IPs serve web:")
            print('|'.join(self.web_reachable))
        else:
            print("No available servers found")

    def run(self):
        self.get_dns_servers()
        self.lookup_ips()
        self.ping()
        self.summarize()
        self.check_web_reachable()
        self.show_results()


class WebRequest(threading.Thread):
    def __init__(self, ip, lock, web_reachable):
        threading.Thread.__init__(self)
        self.ip = ip
        self.lock = lock
        self.web_reachable = web_reachable

    def run(self):
        url = 'http://' + self.ip
        try:
            print('making web request to %s' % url)
            response = urllib.request.urlopen(url, None, 5)
            self.lock.acquire()
            if response.status == 200:
                self.web_reachable.add(self.ip)
            self.lock.release()
        except IOError:
            print("Cannot get data from %s" % url)


class GetDnsServer(threading.Thread):
    def __init__(self, url, lock, dns_servers):
        threading.Thread.__init__(self)
        self.url = url
        self.lock = lock
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
    def __init__(self, name, server, lock, store):
        threading.Thread.__init__(self)
        self.name = name
        self.server = server
        self.lock = lock
        self.store = store

    def run(self):
        try:
            print('looking up %s from %s' % (self.name, self.server))
            output = subprocess.check_output(["nslookup", self.name, self.server])
            ips = self.parse_nslookup_result(output.decode())
            self.lock.acquire()
            for ip in ips:
                # google is heavily blocked in china, most of these official addresses won't work
                if 'google' in self.name and (ip.startswith('74.') or ip.startswith('173.')):
                    continue
                self.store.add(ip)
            self.lock.release()
        except subprocess.CalledProcessError:
            pass

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
    def __init__(self, server, lock, store):
        threading.Thread.__init__(self)
        self.server = server
        self.lock = lock
        self.store = store

    def run(self):
        try:
            print('pinging %s' % (self.server,))
            output = subprocess.check_output(["ping", '-c 10', '-q', self.server])
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


if len(sys.argv) == 2:
    FindMeIP('www.google.com', sys.argv[1]).run()
elif len(sys.argv) == 3:
    FindMeIP(sys.argv[2], sys.argv[1]).run()
else:
    print("Usage:")
    print("Check ip from a certain country(like china): findmeip.py cn")
    print("Check ip for a certain host: findmeip.py cn www.baidu.com")
    print("=" * 50)
    print("Now running default: findmeip.py us www.google.com")
    FindMeIP('www.google.com', 'us').run()
