import urllib
from BeautifulSoup import BeautifulSoup
import re
html = urllib.urlopen('http://www.presidency.ucsb.edu/debates.php').read()
soup = BeautifulSoup(html)
texts = soup.findAll(text=True)
f  = open('transcript4.txt', 'w')
print texts
def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element)):
        return False
    return True

visible_texts = filter(visible, texts)

delete = []
for index, sentence in enumerate(visible_texts):
    if 'Promote Your Page Too' in sentence:
        startIndex = index + 1
    if 'Citation:&nbsp;' in sentence:
        endIndex = index
    if sentence is '':
        delete.append(index)

debate_text = visible_texts[startIndex:endIndex]

for sentence in debate_text:
    f.write(sentence)
    f.write("\n")

f.close()