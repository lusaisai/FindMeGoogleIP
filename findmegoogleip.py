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
import ssl


class FindMeIP:
    def __init__(self, locations):
        self.locations = locations
        self.dns_servers = []
        self.resolved_ips = set()
        self.ping_results = {}
        self.ip_with_time = []
        self.available_ips = []
        self.reachable = []

    @staticmethod
    def read_countries():
        with open(os.path.dirname(os.path.realpath(__file__)) + '/countries.txt') as file:
            return [line.strip() for line in file.readlines() if line.strip()]

    def get_dns_servers(self):
        """Get the public dns server list from public-dns.tk"""
        if self.locations == 'all':
                urls = ['http://public-dns.tk/nameserver/%s.json' % location for location in FindMeIP.read_countries()]
        else:
            urls = ['http://public-dns.tk/nameserver/%s.json' % location for location in self.locations]

        lock = threading.Lock()
        threads = []
        for url in urls:
            if threading.active_count() > 50:
                time.sleep(1)
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
            t = NsLookup('google.com', server, lock, self.resolved_ips)
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

    def check_service(self, servicing):
        lock = threading.Lock()
        threads = []
        for ip in self.available_ips:
            if threading.active_count() > 200:
                time.sleep(1)
            t = ServiceCheck(ip, lock, servicing)
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
        if self.reachable:
            reachable_ip_with_time = [(ip, rtt) for (ip, rtt) in self.ip_with_time if ip in self.reachable]
            print("%d IPs ordered by delay time:" % len(reachable_ip_with_time))
            pprint.PrettyPrinter().pprint(reachable_ip_with_time)
            print("%d IPs concatenated:" % len(self.reachable))
            print('|'.join(self.reachable))
        else:
            print("No available servers found")

    def run(self):
        self.get_dns_servers()
        self.lookup_ips()
        self.ping()
        self.summarize()
        self.check_service(self.reachable)
        self.show_results()


class ServiceCheck(threading.Thread):
    def __init__(self, ip, lock, servicing):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = 443
        self.lock = lock
        self.servicing = servicing

    def run(self):
        try:
            print('checking ssl service %s:%s' % (self.ip, self.port))
            socket.setdefaulttimeout(2)
            conn = ssl.create_default_context().wrap_socket(socket.socket(), server_hostname="www.google.com" )
            conn.connect((self.ip, self.port))
            self.lock.acquire()
            self.servicing.append(self.ip)
            self.lock.release()
        except (ssl.CertificateError, socket.timeout) as err:
            print("error(%s) on connecting %s:%s" % (str(err), self.ip, self.port))


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


if len(sys.argv) >= 2:
        FindMeIP(sys.argv[1:]).run()
else:
    print("Usage:")
    print("Check ip in specified countries: findmegoogleip.py kr us")
    print("=" * 50)
    print("Now running default: find ip from a random chosen country")
    FindMeIP([random.choice(FindMeIP.read_countries())]).run()
