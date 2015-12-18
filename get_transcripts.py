import urllib
from BeautifulSoup import BeautifulSoup
import re
from itertools import chain
from time import sleep
from transcript import Transcript

class Debater():
    '''Separates information from a transcript'''

    def __init__(self, transcript, name):
        self.name = name
        self.date = transcript.date
        self.type = transcript.type
        self.word_count = transcript.counts[name][0]
        self.mention_count = transcript.counts[name][1]
        self.accessory_count = transcript.counts[name][2]
        self.general_sentiment = (transcript.sentiments[name][0] + transcript.sentiments[name][1])/2
        self.political_sentiment= transcript.sentiments[name][2]


def get_transcripts():
    html = urllib.urlopen('http://www.presidency.ucsb.edu/debates.php').read()
    soup = BeautifulSoup(html)
    page = soup.findAll('table', {'width': 740})#[0].findAll('tr')

    table = page[0].findAll('table', {'width': 700})

    debate_link_list = [ele.findAll('a', href=True) for ele in table if ele.find('a') is not None][0]
    debate_links = [link['href'] for link in debate_link_list]

    return debate_links

f = open('training_input.txt', 'w')
comma = ', '
links = get_transcripts()

transcripts = [Transcript(url) for url in links]
debaters = []
for transcript in transcripts:
    print transcript.candidates
    for candidate in transcript.candidates:
        debaters.append(Debater(transcript, candidate))

for debater in debaters:
    print 'name ', debater.name
    print 'date ', debater.date
    print 'type ', debater.type
    print 'words ', debater.word_count
    print 'mentions ', debater.mention_count
    print 'acces ', debater.accessory_count
    f.write(debater.name + comma + debater.date + '\n' + str(debater.word_count) + comma + str(debater.mention_count) + comma + str(debater.accessory_count) + comma + str(debater.general_sentiment) + comma + str(debater.political_sentiment) + '\n')

f.close()

