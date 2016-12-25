#! /usr/bin/python2

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
import urllib2
import settings
import logging
import json


class FindMeGoogleIP:
    BASE_DIR = os.path.dirname(os.path.realpath(__file__))
    DNS_SERVERS_DIR = os.path.join(BASE_DIR, 'dns_servers')

    def __init__(self, locations):
        self.locations = locations
        self.dns_servers = []
        self.resolved_ips = {}
        self.reachable = []
        self.concatenated_result = None
        self.json_result = None
        self.progress_percentage = 0

    @staticmethod
    def read_domains():
        return [f.replace('.txt', '') for f in os.listdir(FindMeGoogleIP.DNS_SERVERS_DIR)]

    def run_threads(self, threads, limit=None):
        """A general way to run multiple threads"""
        if not limit:
            limit = settings.threads
        lock = threading.Lock()
        total = len(threads)
        for index, thread in enumerate(threads):
            thread.lock = lock
            if threading.active_count() > limit:
                time.sleep(1)

            logging.info("Starting thread (%s/%s)" % (index, total))
            self.progress_percentage = (index+1) * 100 / total
            thread.start()

        for thread in threads:
            thread.join()

    def get_dns_servers(self):
        if self.locations == ['all']:
            self.locations = self.read_domains()

        try:
            for location in self.locations:
                domain_file = os.path.join(self.DNS_SERVERS_DIR, location+'.txt')
                logging.info('reading servers from file %s' % domain_file)
                with open(domain_file) as f:
                    data = f.read().strip()
                    if data:
                        servers = re.split('\s+', data)
                        random.shuffle(servers)
                        for server in servers[:settings.servers]:
                            self.dns_servers.append((server, location))
        except IOError:
            logging.error("Cannot read dns servers")

    def lookup_ips(self):
        threads = [NsLookup('google.com', server, self.resolved_ips) for server in self.dns_servers]
        self.run_threads(threads)

    def check_service(self):
        threads = [ServiceCheck(ip, self.resolved_ips[ip][0], self.reachable) for ip in self.resolved_ips.keys()]
        self.run_threads(threads)

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
            self.concatenated_result = '|'.join(ip for ip, rtt in reachable_sorted)
            self.json_result = [ip for ip, rtt in reachable_sorted]

            logging.info("%d IPs ordered by approximate delay time(milliseconds):" % len(reachable_sorted))
            for item in reachable_sorted:
                logging.info((item[0], item[1], self.resolved_ips[item[0]][1]))

            logging.info("%d IPs concatenated:" % len(self.reachable))
            logging.info(self.concatenated_result)

            logging.info("%d IPs in JSON format:" % len(self.reachable))
            logging.info(json.dumps(self.json_result))
        else:
            logging.info("No available servers found")

    def write_into_gae_user_json(self):
        if os.path.isfile(settings.gae_user_json_file) is None:
            return
        if not os.path.isfile(settings.gae_user_json_file):
            logging.error("%s does not exist" % (settings.gae_user_json_file,))
            return

        with open(settings.gae_user_json_file) as f:
            config = json.load(f)
            config['HostMap']['google_hk'] = self.json_result

        with open(settings.gae_user_json_file, 'w') as f:
            json.dump(config, f, sort_keys=True, indent=4, separators=(',', ': '))
            logging.info('Written into %s' % (settings.gae_user_json_file,))

    def run(self):
        self.get_dns_servers()
        self.lookup_ips()
        self.check_service()
        # self.cleanup_low_quality_ips()
        self.show_results()
        self.write_into_gae_user_json()

    def update_dns_files(self):
        threads = [DNSServerFileDownload(location) for location in FindMeGoogleIP.read_domains()]
        self.run_threads(threads, 50)
        logging.info('finished')


class DNSServerFileDownload(threading.Thread):
    def __init__(self, location):
        threading.Thread.__init__(self)
        self.domain = location
        self.url = "http://public-dns.info/nameserver/%s.txt" % location
        self.file = os.path.join(FindMeGoogleIP.DNS_SERVERS_DIR, '%s.txt' % location)
        self.lock = None

    def run(self):
        try:
            logging.info('downloading file %s' % self.url)
            proxy_handler = urllib2.ProxyHandler(proxies=settings.proxies)
            opener = urllib2.build_opener(proxy_handler)
            data = opener.open(self.url, timeout=5).read().decode()
            with open(self.file, mode='w') as f:
                f.write(data)
        except IOError as err:
            logging.error('cannot(%s) update file %s' % (str(err), self.file))


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
            logging.info('checking ssl service %s:%s' % (self.ip, self.port))
            socket.setdefaulttimeout(5)
            conn = ssl.create_default_context().wrap_socket(socket.socket(), server_hostname=self.host)
            conn.connect((self.ip, self.port))

            start = time.time()
            socket.create_connection((self.ip, self.port))
            end = time.time()
            rtt = int((end-start)*1000)  # milliseconds

            with self.lock:
                self.servicing.append((self.ip, rtt))

        except (ssl.CertificateError, ssl.SSLError, socket.timeout, OSError) as err:
            logging.error("error(%s) on connecting %s:%s" % (str(err), self.ip, self.port))


class NsLookup(threading.Thread):
    def __init__(self, name, server, store):
        threading.Thread.__init__(self)
        self.name = name
        self.server = server
        self.lock = None
        self.store = store
        self.resolver = dns.resolver.Resolver()
        self.resolver.nameservers = [self.server[0]]
        self.resolver.lifetime = 5

    def run(self):
        try:
            logging.info('looking up %s from %s' % (self.name, self.server))
            answer = self.resolver.query(self.name)
            with self.lock:
                for response in answer:
                    ip = str(response)
                    if not self.is_spf(ip):
                        self.store[ip] = (self.name, self.server[1])
        except (dns.exception.DNSException, ValueError):
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
    logging.basicConfig(format='%(message)s', level=logging.INFO)
    if len(sys.argv) >= 2:
        if sys.argv[1] == 'update':
            FindMeGoogleIP([]).update_dns_files()
        else:
            FindMeGoogleIP(sys.argv[1:]).run()
    else:
        domain = [random.choice(FindMeGoogleIP.read_domains())]
        logging.info("Usage:")
        logging.info("Find ips in specified domains: findmegoogleip.py kr us")
        logging.info("=" * 50)
        logging.info("Now running default: find ip from a randomly chosen domain: %s" % domain[0])
        FindMeGoogleIP(domain).run()
