from __future__ import division
import urllib
from BeautifulSoup import BeautifulSoup
import re
from itertools import chain
from time import sleep
from transcript import Transcript

class Debater():
    '''Separates information from a transcript'''

    def __init__(self, transcript, name, avg_words, avg_mentions, avg_accessory):#, avg_gensent, avg_polisent):
        self.name = name
        self.date = transcript.date
        self.type = transcript.type
        self.word_count = self.relative(transcript.counts[name][0], avg_words)
        self.mention_count = self.relative(transcript.counts[name][1], avg_mentions)
        self.accessory_count = self.relative(transcript.counts[name][2], avg_accessory)
        # self.general_sentiment = self.relative((transcript.sentiments[name][0][0] + transcript.sentiments[name][1][0])/2, avg_gensent)
        # self.political_sentiment = self.relative(abs(transcript.sentiments[name][2][0] - transcript.sentiments[name][2][3]), avg_polisent)

    def relative(self, value, average):
        if average == 0:
            return 0
        else:
            return (value-average)/average



def get_transcripts():
    html = urllib.urlopen('http://www.presidency.ucsb.edu/debates.php').read()
    soup = BeautifulSoup(html)
    page = soup.findAll('table', {'width': 740})#[0].findAll('tr')

    table = page[0].findAll('table', {'width': 700})

    debate_link_list = [ele.findAll('a', href=True) for ele in table if ele.find('a') is not None][0]
    debate_links = [link['href'] for link in debate_link_list]

    return debate_links

def decompose_transcript(transcript):
    '''
    '''
    sub_debaters = []
    avg_words = 0
    avg_mentions = 0
    avg_accessory = 0
    # avg_gensent = 0
    # avg_polisent = 0

    print transcript.candidates
    num = float(len(transcript.candidates))
    print num
    for candidate in transcript.candidates:
        avg_words += transcript.counts[candidate][0]
        avg_mentions += transcript.counts[candidate][1]
        avg_accessory += transcript.counts[candidate][2]

    avg_words = avg_words/num
    avg_mentions = avg_mentions/num
    avg_accessory = avg_accessory/num
    # avg_gensent = avg_gensent/num
    # avg_polisent = avg_polisent/num


    for candidate in transcript.candidates:
        sub_debaters.append(Debater(transcript, candidate, avg_words, avg_mentions, avg_accessory))#, avg_gensent, avg_polisent))

    return sub_debaters

f = open('training_input.txt', 'w')
comma = ', '
links = get_transcripts()

transcripts = [Transcript(url) for url in [links[12], links[13], links[14], links[36], links[37], links[38], links[75], links[76], links[77], links[81], links[82], links[83]] + links[104:122]]
debaters = []

for transcript in transcripts:
    debaters += decompose_transcript(transcript)

for debater in debaters:
    print 'name ', debater.name
    print 'date ', debater.date
    print 'type ', debater.type
    print 'words ', debater.word_count
    print 'mentions ', debater.mention_count
    print 'acces ', debater.accessory_count
    f.write(debater.name + comma + debater.date + '\n' + str(debater.word_count) + comma + str(debater.mention_count) + comma + str(debater.accessory_count) + '\n')# + comma + str(debater.general_sentiment) + comma + str(debater.political_sentiment) +'\n')

f.close()

