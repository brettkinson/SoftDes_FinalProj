import urllib
from BeautifulSoup import BeautifulSoup
import re
from itertools import chain
from pattern.en import sentiment
import indicoio
indicoio.config.api_key = 'f40bb2f1a1746e98919452261d38003a'

class Transcript():
    ''' Stores a debate transcript and all relevant information for use in predictive
        analysis:

            participants: list of anybody who speaks in the debate
            moderators: list of moderators in the debate
            candidates: list of candidates in the debate
            text: list of paragraphs in debate transcript
            parsed: dictionary of lists of paragraphs spoken mapped to participants
            counts: dictionary of lists of word counts, name mentions, applause, mapped to participants
            sentiments: dictionary of lists of averages of political and general sentiment mapped to participants
    '''
    def __init__(self, url):

        html = urllib.urlopen(url).read()
        soup = BeautifulSoup(html)
        page = soup.findAll('td')

        transcript = self.get_transcript(page)
        self.titles = ['governor ', 'senator ', 'state ', 'representative ', 'house ', 'mr. ', 'mrs. ', 'ms. ', 'president ', 'democratic ', 'republican ', 'independent ', 'admiral ', 'vice ', 'former ', 'moderator ']
        self.text = self.clean_transcript(transcript)
        self.participants = self.get_people(page)
        # self.moderators =
        # self.candidates =
        self.parsed = self.parse_transcript(self.participants, self.text)
        self.counts = self.count_transcript(self.parsed, self.participants)
        # self.sentiments =
        # self.confidence =

    def get_transcript(self, page):
        ''' Finds main text of debate transcript on webpage.

            Returns a list of all paragraphs in the transcript.
        '''
        text = []

        # Create soup object which contains debate transcript section of webpage
        for ele in page:
            if (ele.find('p') is not None) and (ele.find('br') is not None):
                debateBody = ele.findChildren('span', {'class': 'displaytext'}) + ele.findAll('p')
                break

        # Turn soup object into list of lowercase unicode strings
        for para in debateBody:
            text.append(para.findAll(text=True))

        return [ele.lower().encode('utf-8') for ele in list(chain.from_iterable(text))]

    def find_italic(self, page):
        ''' Find content of all italic tags within page, use number of occurences
            to detect names of participants.

            Returns list of participants.
        '''
        italics = {}

        # Find content of all italic tags within debate body
        for ele in page:
            if (ele.find('p') is not None) and (ele.find('p') is not None):
                debateBody = ele.findChildren('span', {'class': 'displaytext'}) + ele.findAll('p')
                break

        # Create a dictionary to count frequency of content
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

        # Return list of content that appears more than twice
        return [key for key in italics if italics[key] > 1]

    def find_bold(self, page):
        ''' Find content of all bold tags within page, use number of occurences
            to detect names of participants.

            Returns list of participants.
        '''
        bolds = {}

        # Find content of all bold tags within debate body
        for ele in page:
            if (ele.find('p') is not None) and (ele.find('p') is not None):
                debateBody = ele.findChildren('span', {'class': 'displaytext'}) + ele.findAll('p')
                break

        #
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

        return [key for key in bolds if bolds[key] > 1]

    def find_normal(self, page):
        ''' Find content of paragraph up to first period or colon, in order to
            identify participants in the debate.

            Returns list of participants.
        '''
        normals = {}

        text = self.get_transcript(page)
        for line in text:
            # Find and remove occurences of standard titles
            for title in self.titles:
                line = line.replace(title, '').strip('"()').lower()

            # Find first occurence of period or colon
            per = line.find('.', 0, 30)
            colon = line.find(':', 0, 30)

            #Determine which occurs first to identify relevant string, and if neither, output full line
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

            # Create dictionary which maps frequency to string
            if nele in normals:
                normals[nele] += 1
            else:
                normals[nele] = 1

        return [key for key in normals if normals[key] > 1]

    def get_people(self, page):

        bolds = self.find_bold(page)
        italics = self.find_italic(page)
        normals = self.find_normal(page)
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
                for title in self.titles:
                    ind = name.find(title)
                    if ind == -1:
                        start = 0
                    else:
                        start = ind + len(title)

                people.append(name[start:-1].strip(':,.').lower().encode('utf-8'))

        return people

    def clean_transcript(self, transcript):
        ''' Remove all titles from the transcript.

            Return cleaned transcript.
        '''
        clean = []

        # Remove titles from transcript
        for line in transcript:
            for title in self.titles:
                line = line.replace(title, '')

            clean.append(line)

        return clean

    def parse_transcript(self, participants, transcript):
        ''' Identify the speaker of each paragraph in the transcript.

            Return a dictionary of list of transcript lines mapped to each participant.
        '''
        parsed = {}

        # Initialize empty lists for each participant in dictionary
        for participant in participants:
            parsed[participant] = []

        parsed['unclaimed'] = []
        prev_par = 'unclaimed'


        for line in transcript:
            claimed = False
            # Search for participant in beginning of paragraph
            for participant in participants:
                # Once found, break loop, set previous speaker
                if participant in line[0:len(participant)]:
                    parsed[participant].append(line[len(participant)+2:])
                    prev_par = participant
                    claimed = True
                    break
            # If no participant found, add to previous participant
            if not claimed:
                parsed[prev_par].append(line)

        return parsed

    def count_transcript(self, parsed, participants):
        ''' Calculate all counting decision variables.

            Returns dictionary of lists which contain:
                [word count, name mentions, applause and laughter]
        '''
        mentions = {}
        words = {}
        noises = {}
        count = {}

        # Initializes counts for each dictionary
        for participant in participants:
            mentions[participant] = 0
            words[participant] = 0
            noises[participant] = 0

        # Count participant mentions in each paragraph
        for para in parsed.values():
            for line in para:
                for participant in participants:
                    if participant in line:
                        mentions[participant] += 1

        # Count words in each participant's entry
        for participant in parsed.keys():
            for line in parsed[participant]:
                try:
                    words[participant] += len(line.split())
                except:
                    pass

                # Count applause or laughter
                if 'applause' in line or 'laughter' in line:
                    noises[participant] += 1
                    parsed[participant].remove(line)

        # Combine dictionaries into one counting dict
        for participant in participants:
            count[participant] = [words[participant], mentions[participant], noises[participant]]

        return count

    def get_sentiment(self, parsed, participants):
        ''' Calculate semtiment values for each line of each participant.

            Returns dictionary of lists containing:
            [sentiment (pattern), sentiment (indico), political sentiment (indico)]
        '''

        senti_patt = {}
        senti_indi = {}
        poli_senti = {}
        senti = 0
        average_count = 0

        for participant in participants:
            senti_patt[participant] = 0
            senti_indi[participant] = 0
            poli_senti[participant] = 0


        for participant in parsed.keys():
            for line in parsed[participant]:
                just_senti = sentiment(line)
                senti += just_senti[0]
                average_count += 1
            senti_patt[participant] = senti/average_count


        senti = 0
        average_count = 0

        for participant in parsed.keys():
            for line in parsed[participant]:
                senti += indicoio.sentiment(line)
                average_count += 1
            senti_indi[participant] = senti/average_count


        conserv = 0
        lib = 0
        average_count = 0

        for participant in parsed.keys():
            for line in parsed[participant]:
                poli_get = indicoio.political(line)
                conserv += poli_get['conservative']
                lib += poli_get['liberal']
                average_count += 1
            poli_senti[participant] = [conserv/average_count, lib/average_count]


        for participant in participants:
            sentiments[participant] = [senti_patt[participant], senti_indi[participant], poli_senti[participant]]

        return sentiments

    def mod_or_cand(self):
        '''
        '''
        qs = {}
        ps = {}
        for participant in self.parsed.keys():
            qs[participant] = 0
            ps[participant] = 0

        for participant in self.parsed.keys():
            for line in self.parsed[participant]:
                qs[participant] += len([1 for char in line if char == '?'])
                ps[participant] += len([1 for char in line if char == '.'])

        return qs, ps


new_transcript = Transcript('http://www.presidency.ucsb.edu/ws/index.php?pid=29408')
for participant in new_transcript.participants:
    for line in new_transcript.parsed[participant]:
            print participant.upper(), line
print new_transcript.mod_or_cand()

