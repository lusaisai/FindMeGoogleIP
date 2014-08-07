FindMeIP
========
Query thousands of dns servers to find the ip of a certain host such as google.


Explain
-------
http://public-dns.tk/ has lots of public dns servers, this script queries them and find available ips.

Usage
-----
By default, it looks up google ips in US,
```bash
./findmeip.py
```

To look up ips in other countries, run these,
```bash
./findmeip.py cn #China
./findmeip.py sg #Singapore
...
```

To look up other hosts, run this,
```bash
./findmeip.py cn baidu.com
```
