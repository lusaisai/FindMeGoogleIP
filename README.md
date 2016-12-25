FindMeGoogleIP
========
Query hundreds of thousands of dns servers to find the google ips.


Explain
-------
<a href="http://public-dns.info/" target="_blank">public-dns.info</a> has lots of public dns servers, this script queries them and find available ips.

Prerequisites
-------
* Python2.7
* Python module dnspython, installed by running the following on command line
```bash
pip install dnspython
```

Usage
-----
By default, it looks up google ips in a randomly chosen domain,
```bash
$ ./findmegoogleip.py
```

To look up ips in specified domains, run this,
```bash
$ ./findmegoogleip.py hk mo tw jp kr
```

To look up ips in all domains, run this,
```bash
$ ./findmegoogleip.py all
```

To update local dns server files, run this,
```bash
$ ./findmegoogleip.py update
```

UI
-----
I would recommend Cygwin on Windows, which gives you the ultimate power to the Linux command line universe.
But if you prefer UI, a simple UI built via Tkinter is available, double click ui.pyw to use it.
![ui screenshot](https://github.com/lusaisai/FindMeGoogleIP/blob/doc/ui.png "ui screenshot")

See below domain map for more domain info</a>.
![domain map](https://github.com/lusaisai/FindMeGoogleIP/blob/doc/domain_map.png "domain map")
