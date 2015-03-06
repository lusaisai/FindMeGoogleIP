FindMeGoogleIP
========
Query hundreds of thousands of dns servers to find the ips of google.


Explain
-------
http://public-dns.tk/ has lots of public dns servers, this script queries them and find available ips.

Python Module Dependencies
-------
```bash
pip3 install dnspython3
```

Usage
-----
By default, it looks up google ips in a randomly chosen domain,
```bash
./findmegoogleip.py
```

To look up ips in specified domains, run this,
```bash
./findmegoogleip.py hk mo tw jp kr
```

To look up ips in all domains, run this,
```bash
./findmegoogleip.py all
```

A simple ui is created for easier use on Windows, just double click ui.pyw

For a complete list, see below domain map/list or browse this <a href="http://ian.macky.net/pat/map/clickable_world.html" target="_blank">world map</a>.

Domain map and list
-------------------
![domain map](https://raw.githubusercontent.com/lusaisai/FindMeGoogleIP/master/domain_map.png "domain map")


```
Asia
====
am Armenia
ae United Arab Emirates
af Afghanistan
as American Samoa
au Australia
az Azerbaijan
bd Bangladesh
bh Bahrain
bn Brunei Darussalam
bt Bhutan
ck Cook Islands
cy Cyprus
fj Fiji
ge Georgia
gu Guam
hk Hong Kong
id Indonesia
il Israel
in India
iq Iraq
ir Iran, Islamic Republic of
jo Jordan
jp Japan
kg Kyrgyzstan
kh Cambodia
ki Kiribati
kr Korea, Republic of
kw Kuwait
kz Kazakhstan
la Lao People's Democratic Republic
lb Lebanon
lk Sri Lanka
mm Myanmar
mn Mongolia
mo Macao
my Malaysia
nc New Caledonia
np Nepal
nr Nauru
nu Niue
nz New Zealand
om Oman
pf French Polynesia
pg Papua New Guinea
ph Philippines
pk Pakistan
ps Palestine, State of
qa Qatar
sa Saudi Arabia
sg Singapore
sy Syrian Arab Republic
th Thailand
tj Tajikistan
tm Turkmenistan
to Tonga
tw Taiwan, Province of China
uz Uzbekistan
vn Viet Nam
ws Samoa
ye Yemen


America
=======
ag Antigua and Barbuda
ai Anguilla
ar Argentina
aw Aruba
bb Barbados
bo Bolivia, Plurinational State of
br Brazil
bs Bahamas
bz Belize
ca Canada
cl Chile
co Colombia
cr Costa Rica
cu Cuba
dm Dominica
do Dominican Republic
ec Ecuador
gd Grenada
gf French Guiana
gl Greenland
gp Guadeloupe
gt Guatemala
gy Guyana
hn Honduras
ht Haiti
jm Jamaica
kn Saint Kitts and Nevis
ky Cayman Islands
lc Saint Lucia
mq Martinique
mx Mexico
ni Nicaragua
pa Panama
pe Peru
pm Saint Pierre and Miquelon
pr Puerto Rico
py Paraguay
sr Suriname
sv El Salvador
tc Turks and Caicos Islands
tt Trinidad and Tobago
us United States
uy Uruguay
vc Saint Vincent and the Grenadines
ve Venezuela, Bolivarian Republic of
vg Virgin Islands, British
vi Virgin Islands, U.S.


Europe
======
ad Andorra
al Albania
at Austria
ba Bosnia and Herzegovina
be Belgium
bg Bulgaria
bm Bermuda
by Belarus
ch Switzerland
cv Cape Verde
cz Czech Republic
de Germany
dk Denmark
ee Estonia
es Spain
fi Finland
fr France
gb United Kingdom
gi Gibraltar
gr Greece
hr Croatia
hu Hungary
ie Ireland
is Iceland
it Italy
li Liechtenstein
lt Lithuania
lu Luxembourg
lv Latvia
mc Monaco
md Moldova, Republic of
mk Macedonia, Republic of
mt Malta
nl Netherlands
no Norway
pl Poland
pt Portugal
ro Romania
ru Russian Federation
se Sweden
si Slovenia
sk Slovakia
sm San Marino
tg Togo
tr Turkey
ua Ukraine
yt Mayotte


Africa
======
ao Angola
bf Burkina Faso
bi Burundi
bj Benin
bw Botswana
cd Congo, The Democratic Republic of the
cf Central African Republic
cg Congo
ci Côte d'Ivoire
cm Cameroon
dj Djibouti
dz Algeria
eg Egypt
er Eritrea
et Ethiopia
ga Gabon
gh Ghana
gm Gambia
gn Guinea
gq Equatorial Guinea
ke Kenya
lr Liberia
ls Lesotho
ly Libya
ma Morocco
mg Madagascar
ml Mali
mr Mauritania
mu Mauritius
mv Maldives
mw Malawi
mz Mozambique
na Namibia
ne Niger
ng Nigeria
re Réunion
rw Rwanda
sc Seychelles
sd Sudan
sl Sierra Leone
sn Senegal
so Somalia
sz Swaziland
tn Tunisia
tz Tanzania, United Republic of
ug Uganda
za South Africa
zm Zambia
zw Zimbabwe
```
