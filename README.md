FindMeIP
========
Query thousands of dns servers to find the ip of a certain host such as google.


Explain
-------
http://public-dns.tk/ has lots of public dns servers, this script queries them and find available ips.

Usage
-----
By default, it looks up google ips in a random chosen country,
```bash
./findmeip.py
```

To look up ips in a specified country, run these, for a complete list, scroll to the end
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
./findmeip.py github.com
```

Country list
```
af Afghanistan
al Albania
dz Algeria
as American Samoa
ad Andorra
ao Angola
ai Anguilla
ag Antigua and Barbuda
ar Argentina
am Armenia
aw Aruba
au Australia
at Austria
az Azerbaijan
bs Bahamas
bh Bahrain
bd Bangladesh
bb Barbados
by Belarus
be Belgium
bz Belize
bj Benin
bm Bermuda
bt Bhutan
bo Bolivia, Plurinational State of
ba Bosnia and Herzegovina
bw Botswana
br Brazil
io British Indian Ocean Territory
bn Brunei Darussalam
bg Bulgaria
bf Burkina Faso
bi Burundi
kh Cambodia
cm Cameroon
ca Canada
cv Cape Verde
ky Cayman Islands
cf Central African Republic
td Chad
cl Chile
cn China
co Colombia
km Comoros
cg Congo
cd Congo, The Democratic Republic of the
ck Cook Islands
cr Costa Rica
hr Croatia
cu Cuba
cy Cyprus
cz Czech Republic
ci Côte d'Ivoire
dk Denmark
dj Djibouti
dm Dominica
do Dominican Republic
ec Ecuador
eg Egypt
sv El Salvador
gq Equatorial Guinea
er Eritrea
ee Estonia
et Ethiopia
fo Faroe Islands
fj Fiji
fi Finland
fr France
gf French Guiana
pf French Polynesia
ga Gabon
gm Gambia
ge Georgia
de Germany
gh Ghana
gi Gibraltar
gr Greece
gl Greenland
gd Grenada
gp Guadeloupe
gu Guam
gt Guatemala
gn Guinea
gw Guinea-Bissau
gy Guyana
ht Haiti
va Holy See (Vatican City State)
hn Honduras
hk Hong Kong
hu Hungary
is Iceland
in India
id Indonesia
ir Iran, Islamic Republic of
iq Iraq
ie Ireland
il Israel
it Italy
jm Jamaica
jp Japan
jo Jordan
kz Kazakhstan
ke Kenya
ki Kiribati
kp Korea, Democratic People's Republic of
kr Korea, Republic of
kw Kuwait
kg Kyrgyzstan
la Lao People's Democratic Republic
lv Latvia
lb Lebanon
ls Lesotho
lr Liberia
ly Libya
li Liechtenstein
lt Lithuania
lu Luxembourg
mo Macao
mk Macedonia, Republic of
mg Madagascar
mw Malawi
my Malaysia
mv Maldives
ml Mali
mt Malta
mh Marshall Islands
mq Martinique
mr Mauritania
mu Mauritius
yt Mayotte
mx Mexico
fm Micronesia, Federated States of
md Moldova, Republic of
mc Monaco
mn Mongolia
ms Montserrat
ma Morocco
mz Mozambique
mm Myanmar
na Namibia
nr Nauru
np Nepal
nl Netherlands
nc New Caledonia
nz New Zealand
ni Nicaragua
ne Niger
ng Nigeria
nu Niue
no Norway
om Oman
pk Pakistan
pw Palau
ps Palestine, State of
pa Panama
pg Papua New Guinea
py Paraguay
pe Peru
ph Philippines
pl Poland
pt Portugal
pr Puerto Rico
qa Qatar
ro Romania
ru Russian Federation
rw Rwanda
re Réunion
sh Saint Helena, Ascension and Tristan da Cunha
kn Saint Kitts and Nevis
lc Saint Lucia
pm Saint Pierre and Miquelon
vc Saint Vincent and the Grenadines
ws Samoa
sm San Marino
sa Saudi Arabia
sn Senegal
sc Seychelles
sl Sierra Leone
sg Singapore
sk Slovakia
si Slovenia
sb Solomon Islands
so Somalia
za South Africa
es Spain
lk Sri Lanka
sd Sudan
sr Suriname
sz Swaziland
se Sweden
ch Switzerland
sy Syrian Arab Republic
tw Taiwan, Province of China
tj Tajikistan
tz Tanzania, United Republic of
th Thailand
tg Togo
tk Tokelau
to Tonga
tt Trinidad and Tobago
tn Tunisia
tr Turkey
tm Turkmenistan
tc Turks and Caicos Islands
tv Tuvalu
ug Uganda
ua Ukraine
ae United Arab Emirates
gb United Kingdom
us United States
uy Uruguay
uz Uzbekistan
vu Vanuatu
ve Venezuela, Bolivarian Republic of
vn Viet Nam
vg Virgin Islands, British
vi Virgin Islands, U.S.
wf Wallis and Futuna
ye Yemen
zm Zambia
zw Zimbabwe
```
