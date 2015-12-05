import urllib
from BeautifulSoup import BeautifulSoup
import re
from itertools import chain
from time import sleep

html = urllib.urlopen('http://www.presidency.ucsb.edu/debates.php').read()
soup = BeautifulSoup(html)
page = soup.findAll('table', {'width': 740})#[0].findAll('tr')

table = page[0].findAll('table', {'width': 700})

debate_link_list = [ele.findAll('a', href=True) for ele in table if ele.find('a') is not None][0]
debate_links = [link['href'] for link in debate_link_list]
print debate_links