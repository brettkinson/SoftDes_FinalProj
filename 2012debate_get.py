import urllib
from BeautifulSoup import BeautifulSoup
import re
from itertools import chain
from time import sleep
# import indicoio

# indicoio.config.api_key = 'f40bb2f1a1746e98919452261d38003a'
# f  = open('transcript.txt', 'w')
html = urllib.urlopen('http://www.presidency.ucsb.edu/ws/index.php?pid=96683').read()
soup = BeautifulSoup(html)
page = soup.findAll('td')

titles = ['governor ', 'senator ', 'state ', 'representative ', 'house ', 'mr. ', 'mrs. ', 'ms. ', 'president ', 'democratic ', 'republican ', 'independent ', 'admiral ', 'vice', 'former', 'moderator ']

def get_transcript(page):
    text = []
    for ele in page:
        if (ele.find('p') is not None) and (ele.find('br') is not None):
            debateBody = ele.findChildren('span', {'class': 'displaytext'}) + ele.findAll('p')
            break

    for para in debateBody:
        text.append(para.findAll(text=True))

    return [ele.lower() for ele in list(chain.from_iterable(text))]

def find_italic(page):
    ''' '''
    italics = {}
    for ele in page:
        if (ele.find('p') is not None) and (ele.find('p') is not None):
            debateBody = ele.findChildren('span', {'class': 'displaytext'}) + ele.findAll('p')
            break

    for para in debateBody:
        if para.find('i') is not None:

            try:
                itele = para.findAll('i')[0].contents[0]

                if itele in italics:
                    italics[itele] += 1
                else:
                    italics[itele] = 1

            except:
                pass

    people = [key for key in italics if italics[key] > 2]
    return people

def get_transcript_list():
    html = urllib.urlopen('http://www.presidency.ucsb.edu/debates.php').read()
    soup = BeautifulSoup(html)
    page = soup.findAll('table', {'width': 740})#[0].findAll('tr')

    table = page[0].findAll('table', {'width': 700})

    debate_link_list = [ele.findAll('a', href=True) for ele in table if ele.find('a') is not None][0]
    debate_links = [link['href'] for link in debate_link_list]

    return debate_links

def find_bold(page):
    bolds = {}
    for ele in page:
        if (ele.find('p') is not None) and (ele.find('p') is not None):
            debateBody = ele.findChildren('span', {'class': 'displaytext'}) + ele.findAll('p')
            break

    for para in debateBody:
        if para.find('b') is not None:

            try:
                bele = para.findAll('b', text=True)[0]

                if bele in bolds:
                    bolds[bele] += 1
                else:
                    bolds[bele] = 1

            except:
                pass

    people = [key for key in bolds if bolds[key] > 2]
    return people

def find_normal(page):
    normals = {}
    text = get_transcript(page)
    for line in text:
        for title in titles:
            line = line.replace(title, '').strip('"()').lower()

        per = line.find('.', 0, 30)
        colon = line.find(':', 0, 30)

        if per == -1 and colon == -1:
            nele = line
        elif per == -1 and colon != -1:
            nele = line[0:colon]
        elif per != -1 and colon == -1:
            nele = line[0:per]
        elif per < colon:
            nele = line[0:per]
        else:
            nele = line[0:colon]

        if nele in normals:
            normals[nele] += 1
        else:
            normals[nele] = 1

    people = [key for key in normals if normals[key] > 2]
    return people

def get_people(page, titles):

    bolds = find_bold(page)
    italics = find_italic(page)
    normals = find_normal(page)
    people = []

    if bolds == [] and italics == []:
        peeps = normals
        people = [peep for peep in peeps if 'applause' not in peep]
        people = [peep for peep in people if 'laughter' not in peep]
    else:
        if italics != []:
            peeps = italics
        if bolds != []:
            peeps = bolds

        for name in peeps:
            for title in titles:
                ind = name.find(title)
                if ind == -1:
                    start = 0
                else:
                    start = ind + len(title)

            people.append(name[start:-1].strip(':,.').lower())

    return people

def clean_transcript(transcript, titles):
    clean = []
    for line in transcript:
        for title in titles:
            line = line.replace(title, '')
        clean.append(line)

    return clean

def parse_transcript(participants, transcript):
    parsed = {}

    for participant in participants:
        parsed[participant] = []

    parsed['unclaimed'] = []
    prev_par = 'unclaimed'
    for line in transcript:
        claimed = False
        for participant in participants:
            if participant in line[0:len(participant)]:
                parsed[participant].append(line[len(participant)+2:])
                prev_par = participant
                claimed = True
                break

        if not claimed:
            parsed[prev_par].append(line)

    return parsed

def count_transcript(parsed, participants):
    '''
    '''
    mentions = {}
    words = {}
    noises = {}
    count = {}

    for participant in participants:
        mentions[participant] = 0
        words[participant] = 0
        noises[participant] = 0

    for para in parsed.values():
        for line in para:
            for participant in participants:
                if participant in line:
                    mentions[participant] += 1

    for participant in parsed.keys():
        for line in parsed[participant]:
            try:
                words[participant] += len(line.split())
            except:
                pass

            if 'applause' in line or 'laughter' in line:
                noises[participant] += 1

    for participant in participants:
        count[participant] = [words[participant], mentions[participant], noises[participant]]

    return count


transcript = get_transcript(page)
participants = get_people(page, titles)
clean_transcript = clean_transcript(transcript, titles)
parsed = parse_transcript(participants, clean_transcript)

for key in parsed:
    for line in parsed[key]:
        try:
            print key, line, '\n'
        except:
            pass

print count_transcript(parsed, participants)

