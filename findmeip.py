#! /usr/bin/python3
import random
import urllib.request
import json
import subprocess
import threading
import sys
import pprint
import time
import os
import socket


class FindMeIP:
    def __init__(self, hostname, location):
        self.hostname = hostname
        self.location = location
        self.dns_servers = []
        self.resolved_ips = set()
        self.ping_results = {}
        self.ip_with_time = []
        self.available_ips = set()
        self.web_reachable = set()
        self.cloud_reachable = set()

    @staticmethod
    def read_countries():
        with open(os.path.dirname(os.path.realpath(__file__)) + '/countries.txt') as file:
            return [line.strip() for line in file.readlines() if line.strip()]

    def get_dns_servers(self):
        """Get the public dns server list from public-dns.tk"""
        if self.location == 'all':
                urls = ['http://public-dns.tk/nameserver/%s.json' % location for location in FindMeIP.read_countries()]
        else:
            urls = ['http://public-dns.tk/nameserver/%s.json' % self.location]

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

    def check_service(self, port, servicing):
        lock = threading.Lock()
        threads = []
        for ip in self.available_ips:
            if threading.active_count() > 200:
                time.sleep(1)
            t = ServiceCheck(ip, port, lock, servicing)
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
            print("%d IPs ordered by delay time:" % len(self.ip_with_time))
            pprint.PrettyPrinter().pprint(self.ip_with_time)
            print("%d IPs serve web:" % len(self.web_reachable))
            print('|'.join(self.web_reachable))
            print("%d IPs serve cloud:" % len(self.cloud_reachable))
            print('|'.join(self.cloud_reachable))
        else:
            print("No available servers found")

    def run(self):
        self.get_dns_servers()
        self.lookup_ips()
        self.ping()
        self.summarize()
        self.check_service(80, self.web_reachable)
        self.check_service(443, self.cloud_reachable)
        self.show_results()


class ServiceCheck(threading.Thread):
    def __init__(self, ip, port, lock, servicing):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.lock = lock
        self.servicing = servicing

    def run(self):
        try:
            print('check service %s:%s' % (self.ip, self.port))
            socket.create_connection((self.ip, self.port), 1)
            self.lock.acquire()
            self.servicing.add(self.ip)
            self.lock.release()
        except socket.timeout:
            print("%s is not serving on port %s" % (self.ip, self.port))


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
    if '.' in sys.argv[1]:
        FindMeIP(sys.argv[1], random.choice(FindMeIP.read_countries())).run()
    else:
        FindMeIP('www.google.com', sys.argv[1]).run()
elif len(sys.argv) == 3:
    FindMeIP(sys.argv[1], sys.argv[2]).run()
else:
    print("Usage:")
    print("Check ip from a certain country(like china): findmeip.py cn")
    print("Check ip for a certain host: findmeip.py github.com")
    print("Check ip for a certain host from a certain country: findmeip.py github.com us")
    print("=" * 50)
    print("Now running default: find ip of www.google.com from a random country")
    FindMeIP('www.google.com', random.choice(FindMeIP.read_countries())).run()
