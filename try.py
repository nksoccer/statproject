import urllib2
from lxml import html

FILM_INDEX = "http://www.films101.com/yl5r.htm"
content = urllib2.urlopen(FILM_INDEX).read()
tree = html.fromstring(content)
print(content)
names = tree.xpath('//table/tr/td/a[@title]/text()')
print(names)
