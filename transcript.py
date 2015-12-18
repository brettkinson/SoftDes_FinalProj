import urllib
from BeautifulSoup import BeautifulSoup
import re
from itertools import chain
from pattern.en import sentiment
import indicoio
from scipy import std

indicoio.config.api_key = '01106080f7ebca4b93caec65a04c4b61'

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
        ''' Init script, runs methods to create full Transcript object.

            Input:
                url: (str) url of debate transcript to parsed
        '''

        html = urllib.urlopen(url).read()
        soup = BeautifulSoup(html)
        self.type = self.get_type(soup)
        self.date = soup.find('span', {'class': 'docdate'}).text.encode('utf-8')
        self.page = soup.findAll('td')
        transcript = self.get_transcript(self.page)
        self.titles = ['governor ', 'senator ', 'state ', 'representative ', 'house ', 'mr. ', 'mrs. ', 'ms. ', 'democratic ', 'republican ', 'independent ', 'admiral ', 'vice ', 'former ', 'moderator ', 'sen. ', 'rep. ']
        self.text = self.clean_transcript(transcript)
        self.participants = self.get_people(self.page)
        self.candidates = []
        self.moderators = []
        self.parsed = self.parse_transcript(self.participants, self.text)
        self.counts = self.count_transcript(self.parsed, self.participants)
        self.mod_or_cand()
        self.sentiments = self.get_sentiment(self.parsed, self.candidates)
        # self.confidence =

    def get_type(self, soup):
        ''' Find header text to classify debate.

            Input:
            page: (BeautifulSoup object) text of page
        '''
        deb_type = soup.find('span', {'class': 'paperstitle'}).text.lower().encode('utf-8')

        if 'democrat' in deb_type:
            self.type = 'democrat'
        elif 'republican' in deb_type:
            self.type = 'republican'
        elif 'vice' in deb_type:
            self.type = 'vice'
        else:
            self.type = 'presidential'



    def get_transcript(self, page):
        ''' Finds main text of debate transcript on webpage.

            Input:
                page: (BeautifulSoup object) text of page

            Returns:
                (list) all paragraphs in the transcript.
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

            Input:
                page: (BeautifulSoup object) text of page

            Returns:
                (list) italic namess
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
        return [key.lower() for key in italics if italics[key] > 1]

    def find_bold(self, page):
        ''' Find content of all bold tags within page, use number of occurences
            to detect names of participants.

            Input:
                page: (BeautifulSoup object) text of page

            Returns:
                (list) boldface names
        '''
        bolds = {}

        # Find content of all bold tags within debate body
        for ele in page:
            if (ele.find('p') is not None) and (ele.find('p') is not None):
                debateBody = ele.findChildren('span', {'class': 'displaytext'}) + ele.findAll('p')
                break

        # Create a dictionary to count frequency of content
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

        return [key.lower() for key in bolds if bolds[key] > 1]

    def find_normal(self, page):
        ''' Find content of paragraph up to first period or colon, in order to
            identify participants in the debate.

            Input:
                page: (BeautifulSoup object) text of page

            Returns:
                (list) identified names
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
        ''' Use results of name searches to determine final participants.

            Input:
                page: (BeautifulSoup object) text of page

            Returns:
                (list) final participants
        '''
        # Find potential name options
        bolds = self.find_bold(page)
        italics = self.find_italic(page)
        normals = self.find_normal(page)
        people = []

        # Decide between parsing method
        if bolds == [] and italics == []:
            print 'using normals'
            peeps = normals
            people = [peep for peep in peeps if 'applause' not in peep]
            people = [peep for peep in people if 'laughter' not in peep]
            people = [peep for peep in people if '\n' not in peep]
        else:
            if bolds != []:
                peeps = bolds
                print 'using bolds'
            elif italics != []:
                peeps = italics
                print 'using italics'

            # Remove titles from names
            for name in peeps:
                for title in self.titles:
                    ind = name.find(title)
                    if ind == -1:
                        start = 0
                    else:
                        start = ind + len(title)
                        break
                clean_name = name[start:-1].strip(':,.')
                if clean_name != '':
                    people.append(clean_name)

        print self.date
        return people

    def clean_transcript(self, transcript):
        ''' Remove all titles from the transcript.

            Input:
                transcript: (list of lists) transcript text
            Returns:
                (list of lists) cleaned transcript.
        '''
        clean = []

        # Remove titles from transcript
        for line in transcript:
            for title in self.titles:
                line = line.replace(title, '')

            clean.append(line)

        return clean

    def parse_transcript(self, participants, transcript):
        ''' Identify the speaker of each paragraph in the transcript, and
            organize that information information a list.

            Inputs:
                participant: (list) debate participants
                transcript: (list of lists) debate text

            Returns:
                parsed: (dict) dictionary mapping lines to speakers
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
                # Once found, break loop, set as previous speaker
                if participant in line[0:len(participant)+1]:
                    # print participant, 'claimed'
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

            Inputs:
                participants: (list) debate participants
                parsed: (dict of lists) parsed transcript

            Returns:
                (dict of lists) with word count, name mentions, applause and laughter
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
                try:
                    if 'applause' in line or 'laughter' in line:
                        noises[participant] += 1
                        parsed[participant].remove(line)
                except:
                    pass

        # Combine dictionaries into one counting dict
        for participant in participants:
            count[participant] = [words[participant], mentions[participant], noises[participant]]

        return count

    def get_sentiment(self, parsed, participants):
        ''' Calculate semtiment values for each line of each participant.

            Inputs:
                parsed: (dict of lists) mapping line to speaker
                participants: (list) every speaker in debate

            Returns:
                (dict of lists) containing sentiment (pattern), sentiment (indico),
                political sentiment (indico)]
        '''

        # Pre-allocating variables, etc
        sentiments = {}
        senti_patt = {}
        senti_indi = {}
        poli_senti = {}
        senti = 0
        average_count = 0

        for participant in participants:
            senti_patt[participant] = 0
            senti_indi[participant] = 0
            poli_senti[participant] = 0

        # Running pattern sentiment on each line for each participant
        for participant in participants:
            senti_max = 0
            senti_min = 0
            just_senti = 0
            for line in parsed[participant]:
                just_senti = sentiment(line)
                senti += just_senti[0]
                average_count += 1 # Total line count, to use to average
                if just_senti[0] > senti_max: #Finding max and min values
                    senti_max = just_senti[0]
                if just_senti[0] < senti_min:
                    senti_min = just_senti[0]

            # Writing average sentiment and max/min data to return
            senti_patt[participant] = [(senti/average_count+1)/2.0, (senti_max+1)/2.0, (senti_min+1)/2.0]

        # Running indico sentiment on each line for each participant
        for participant in participants:
            senti_max = 0
            senti_min = 0
            senti = 0
            average_count = 0
            it = 0 # Debug counter
            curr_senti = 0
            for line in parsed[participant]:
                print it
                try:
                    curr_senti = indicoio.sentiment(line)
                    senti += curr_senti
                    average_count += 1
                except:
                    pass
                it += 1

                # Finding max and min values
                if curr_senti > senti_max:
                    senti_max = curr_senti
                if curr_senti < senti_min:
                    senti_min = curr_senti

            senti_indi[participant] = [senti/average_count, senti_max, senti_min] #writing average sentiment and max/min data to return

        for participant in participants:
            max_con = 0
            min_con = 0
            max_lib = 0
            min_lib = 0

            # Determining political sentiment for each participant
            conserv = 0
            lib = 0
            average_count = 0
            poli_get = {'Conservative': 0, 'Liberal': 0}
            for line in parsed[participant]:
                print it
                try: # Attempts to call poli sentiment function on each line
                    poli_get = indicoio.political(line)
                    conserv += poli_get['Conservative'] # Adds to each count
                    lib += poli_get['Liberal']
                    average_count += 1
                except:
                    pass

                it += 1
                if max_con > poli_get['Conservative']: # Sets max and min values as it cycles through
                    max_con = poli_get['Conservative']
                if min_con < poli_get['Conservative']:
                    min_con = poli_get['Conservative']
                if max_lib > poli_get['Liberal']:
                    max_lib = poli_get['Liberal']
                if min_lib < poli_get['Liberal']:
                    min_lib = poli_get['Liberal']

            poli_senti[participant] = [conserv/average_count, max_con, min_con, lib/average_count, max_lib, min_lib]

        # Creating output dictionary with all data collected
        for participant in participants:
            sentiments[participant] = [senti_patt[participant], senti_indi[participant], poli_senti[participant]]

        return sentiments

    def get_that_header(self):
        ''' Find header tag for name recognition.

            Returns:
                (lists) potential moderators, potential candidates
        '''

        header = []
        potent_mod = []
        potent_cand = []

        # Find content of all bold tags within debate body
        for ele in self.page:
            if (ele.find('p') is not None) and (ele.find('p') is not None):
                debateBody = ele.findChildren('span', {'class': 'displaytext'}) + ele.findAll('p')
                break

        for para in debateBody:
            if para.find('b') is not None:
                header.append(para.findChildren('b', text=True))

        for ele in header:
            mod_ele = [subele.lower().encode('utf-8') for subele in ele]
            # Find text in line with bold 'moderator' tag
            if 'moderator' in mod_ele[0] or 'host' in mod_ele[0]:
                for human in mod_ele[1:]:
                    potent_mod.append(human)

            # Find text in line with bold 'participant' tag
            elif 'participant' in mod_ele[0]:
                for human in mod_ele[1:]:
                    potent_cand.append(human)

        return  potent_cand, potent_mod


    def mod_or_cand(self):
        ''' Distinguish between participants as either moderators/other and
            candidates.

            Returns:
                Modifies candidates and moderators attributes.
        '''

        # Attempt to use information from header first
        potent_cand, potent_mod = self.get_that_header()

        if potent_cand != [] and potent_mod != []:
            print "There's a header"
            #Check if participant in the header
            for participant in self.parsed.keys():
                for ele in potent_cand:
                    if participant in ele:
                        self.candidates.append(participant)
                for ele in potent_mod:
                    if participant in potent_mod:
                        self.moderators.append(participant)

            for candidate in self.candidates:
                print '    ', candidate, self.counts[candidate]
            return

        # If there's no header, proceed with the following semi-statistical analysis
        print 'No header'
        lens = {}
        for participant in self.parsed.keys():
            lens[participant] = []

        # Calculate length of participant phrases
        for participant in self.parsed.keys():
            for line in self.parsed[participant]:
                lens[participant].append(len(line.split()))

        for participant in lens.keys():
            # Delete extraneous participants
            if lens[participant] == [] or participant == 'unclaimed':
                del lens[participant]
            # Calculate average phrase length
            else:
                lens[participant] = sum(lens[participant])/len(lens[participant])

        # Calculate standard deviations, threshold for word count, phrase length
        length_dev = std(lens.values())
        length_most = max(lens.values())
        length_thresh = length_most-(2.8*length_dev)

        count_dev = std([self.counts[participant][0] for participant in lens.keys()])
        count_most = max([self.counts[participant][0] for participant in lens.keys()])
        count_thresh = count_most-(1.5*count_dev)

        # Filter out moderators from candidates
        for participant in lens.keys():
            if lens[participant] < length_thresh or self.counts[participant][0] < count_thresh:
                self.moderators.append(participant)
            else:
                self.candidates.append(participant)

        for candidate in self.candidates:
            print '    ', candidate, self.counts[candidate]

if __name__ == '__main__':
    new_transcript = Transcript('http://www.presidency.ucsb.edu/ws/index.php?pid=110756')
    # for participant in new_transcript.participants:
    #     for line in new_transcript.parsed[participant]:
                # print participant.upper(), line
    # new_transcript.mod_or_cand()
    print new_transcript.candidates
    print new_transcript.counts
    # print new_transcript.sentiments
