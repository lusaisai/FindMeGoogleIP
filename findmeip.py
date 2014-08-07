#! /usr/bin/python3

import urllib.request
import json
import subprocess
import threading
import sys
import pprint


class FindMeIP:
    def __init__(self, hostname, country):
        self.hostname = hostname
        self.country = country
        self.dns_servers = []
        self.resolved_ips = set()
        self.ping_results = {}

    def get_dns_servers(self):
        """Get the public dns server list from public-dns.tk"""
        if self.country == 'all':
            url = 'http://public-dns.tk/nameservers.json'
        else:
            url = 'http://public-dns.tk/nameserver/%s.json' % self.country
        print("Getting the list of dns servers from %s" % url)
        try:
            data = urllib.request.urlopen(url).read().decode()
            servers = json.loads(data)
            for server in servers:
                if server['state'] == 'valid' and '.' in server['ip']:
                    self.dns_servers.append(server['ip'])
        except IOError:
            print("Cannot get data from %s" % url)
            exit(1)

    def lookup_ips(self):
        lock = threading.Lock()
        threads = []
        for server in self.dns_servers:
            t = NsLookup(self.hostname, server, lock, self.resolved_ips)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

    def ping(self):
        lock = threading.Lock()
        threads = []
        for ip in self.resolved_ips:
            t = Ping(ip, lock, self.ping_results)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

    def show_results(self):
        loss_less = []
        for k, v in self.ping_results.items():
            if v['loss'] == 0:
                loss_less.append((k, v['time']))
        if loss_less:
            pprint.PrettyPrinter().pprint(sorted(loss_less, key=lambda x: x[1]))
        else:
            print("No available servers found")

    def run(self):
        self.get_dns_servers()
        self.lookup_ips()
        self.ping()
        self.show_results()


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
        time = result.split('\n')[-2].split(' = ')[-1].split('/')[1]
        return {'loss': float(loss), 'time': float(time)}

if len(sys.argv) == 2:
    FindMeIP('www.google.com', sys.argv[1]).run()
elif len(sys.argv) == 3:
    FindMeIP(sys.argv[2], sys.argv[1]).run()
else:
    print("Usage:")
    print("Check ip from a certain country(like china): findmeip.py cn")
    print("Check ip for a certain host: findmeip.py cn www.baidu.com")
    print("Now running default: findmeip.py us www.google.com")
    FindMeIP('www.google.com', 'us').run()
