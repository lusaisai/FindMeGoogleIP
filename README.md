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

To look up ips in other countries, run these, for a complete list, scroll to the end
```bash
./findmeip.py cn #China
./findmeip.py sg #Singapore
./findmeip.py au #Australia
...
```

To look up ips in all countries, run this,
```bash
./findmeip.py all
```

To look up other hosts, run this,
```bash
./findmeip.py cn baidu.com
```

Country list
```
af Afghanistan
al Albania
dz Algeria
ag Antigua and Barbuda
ar Argentina
am Armenia
au Australia
at Austria
az Azerbaijan
bs Bahamas
bh Bahrain
bd Bangladesh
by Belarus
be Belgium
bm Bermuda
bo Bolivia, Plurinational State of
ba Bosnia and Herzegovina
br Brazil
bg Bulgaria
ca Canada
cl Chile
cn China
co Colombia
hr Croatia
cz Czech Republic
dk Denmark
do Dominican Republic
ec Ecuador
eg Egypt
sv El Salvador
er Eritrea
ee Estonia
fi Finland
fr France
ga Gabon
ge Georgia
de Germany
gh Ghana
gi Gibraltar
gr Greece
gt Guatemala
hn Honduras
hk Hong Kong
hu Hungary
is Iceland
in India
id Indonesia
ir Iran, Islamic Republic of
ie Ireland
il Israel
it Italy
jm Jamaica
jp Japan
jo Jordan
kz Kazakhstan
ke Kenya
kr Korea, Republic of
kw Kuwait
kg Kyrgyzstan
lv Latvia
ly Libya
li Liechtenstein
lt Lithuania
lu Luxembourg
mo Macao
mk Macedonia, Republic of
my Malaysia
mt Malta
mr Mauritania
mx Mexico
md Moldova, Republic of
mc Monaco
mn Mongolia
np Nepal
nl Netherlands
nz New Zealand
ni Nicaragua
ng Nigeria
no Norway
om Oman
pk Pakistan
ps Palestine, State of
py Paraguay
pe Peru
ph Philippines
pl Poland
pt Portugal
pr Puerto Rico
ro Romania
ru Russian Federation
pm Saint Pierre and Miquelon
sm San Marino
sa Saudi Arabia
sg Singapore
sk Slovakia
si Slovenia
za South Africa
es Spain
se Sweden
ch Switzerland
tw Taiwan, Province of China
th Thailand
tn Tunisia
tr Turkey
ua Ukraine
gb United Kingdom
us United States
uy Uruguay
ve Venezuela, Bolivarian Republic of
vn Viet Nam
```