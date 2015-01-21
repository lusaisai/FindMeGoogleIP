FindMeIP
========
Query thousands of dns servers to find the ips of google.


Explain
-------
http://public-dns.tk/ has lots of public dns servers, this script queries them and find available ips.

Usage
-----
By default, it looks up google ips in a random chosen domain,
```bash
./findmeip.py
```

To look up ips in specified domains, run these, for a complete list, scroll to the end
```bash
./findmeip.py sg au #Singapore and Australia
...
```

To look up ips in all domains, run this,
```bash
./findmeip.py all
```

Domain list
```
Asia
====
am Armenia
la Lao People's Democratic Republic
mn Mongolia
jp Japan
ir Iran, Islamic Republic of
ge Georgia
uz Uzbekistan
tw Taiwan, Province of China
sg Singapore
kr Korea, Republic of
sa Saudi Arabia
mm Myanmar
qa Qatar
kh Cambodia
cy Cyprus
om Oman
ph Philippines
mo Macao
kw Kuwait
in India
np Nepal
pk Pakistan
af Afghanistan
il Israel
id Indonesia
hk Hong Kong
vn Viet Nam
tj Tajikistan
ae United Arab Emirates
bd Bangladesh
sy Syrian Arab Republic
lk Sri Lanka
bn Brunei Darussalam
kg Kyrgyzstan
lb Lebanon
th Thailand
az Azerbaijan
bh Bahrain
iq Iraq
tm Turkmenistan
kz Kazakhstan
jo Jordan
ye Yemen
bt Bhutan
to Tonga
ki Kiribati
pf French Polynesia
ck Cook Islands
as American Samoa
nc New Caledonia
nu Niue
nr Nauru
gu Guam
fj Fiji
ws Samoa
au Australia
my Malaysia
nz New Zealand
pg Papua New Guinea
ps Palestine, State of


America
=======
ca Canada
hn Honduras
vc Saint Vincent and the Grenadines
vi Virgin Islands, U.S.
lc Saint Lucia
ai Anguilla
kn Saint Kitts and Nevis
do Dominican Republic
cl Chile
pr Puerto Rico
ht Haiti
tt Trinidad and Tobago
sr Suriname
pa Panama
bs Bahamas
uy Uruguay
pm Saint Pierre and Miquelon
mx Mexico
mq Martinique
ni Nicaragua
us United States
pe Peru
bo Bolivia, Plurinational State of
jm Jamaica
cu Cuba
gy Guyana
ec Ecuador
gt Guatemala
gp Guadeloupe
gd Grenada
tc Turks and Caicos Islands
gl Greenland
sv El Salvador
dm Dominica
cr Costa Rica
ky Cayman Islands
gf French Guiana
ve Venezuela, Bolivarian Republic of
co Colombia
bz Belize
bb Barbados
py Paraguay
aw Aruba
ar Argentina
ag Antigua and Barbuda
vg Virgin Islands, British
br Brazil


Europe
======
de Germany
pt Portugal
es Spain
ch Switzerland
hr Croatia
pl Poland
lt Lithuania
at Austria
li Liechtenstein
al Albania
ee Estonia
se Sweden
bg Bulgaria
mk Macedonia, Republic of
ba Bosnia and Herzegovina
sm San Marino
it Italy
lv Latvia
cz Czech Republic
fr France
yt Mayotte
tg Togo
no Norway
ru Russian Federation
mc Monaco
by Belarus
mt Malta
lu Luxembourg
gb United Kingdom
si Slovenia
ua Ukraine
tr Turkey
fi Finland
gi Gibraltar
ie Ireland
dk Denmark
md Moldova, Republic of
hu Hungary
ro Romania
be Belgium
sk Slovakia
gr Greece
ad Andorra
nl Netherlands
is Iceland
cv Cape Verde
bm Bermuda


Africa
======
na Namibia
tn Tunisia
ly Libya
bj Benin
bf Burkina Faso
mr Mauritania
ne Niger
ke Kenya
lr Liberia
so Somalia
sz Swaziland
ls Lesotho
mz Mozambique
gq Equatorial Guinea
zm Zambia
ao Angola
ga Gabon
ng Nigeria
rw Rwanda
sd Sudan
ug Uganda
za South Africa
zw Zimbabwe
bw Botswana
sl Sierra Leone
cm Cameroon
dj Djibouti
tz Tanzania, United Republic of
sn Senegal
gn Guinea
ma Morocco
eg Egypt
bi Burundi
cg Congo
mw Malawi
gm Gambia
cf Central African Republic
ml Mali
er Eritrea
dz Algeria
et Ethiopia
gh Ghana
ci Côte d'Ivoire
re Réunion
mu Mauritius
mv Maldives
sc Seychelles
mg Madagascar
cd Congo, The Democratic Republic of the
```
