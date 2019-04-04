import re
import pandas as pd
from pandas import ExcelWriter

class TextProcessor:

    # Abstract and Affilitation matcher returns list of authors linked with affliations
    def author_affli_matcher(self, autdet, afdet):
        al = re.split(',(?![0-9])', autdet.replace('\n', ''))
        al = al[0:-1]+ al[-1].split(' & ')
        print('Authors:', autdet, '\n', al)
        afl = re.split(r';\s?(?=[0-9])', afdet.replace('\n', ''))
        print('Afli:', afdet, '\n', afl)
        contains_nums = re.findall(r'[0-9]+', autdet)
        # if no commas are present and number of words seperaed by ( ) is >4 not an author
        if len(al) == 1 and len(al[0].split(' ')) > 4: raise Exception('Not a vlaid author')
        print('AUTHOR FFLI TESTER', len(al), al)
        det = []
        if contains_nums:
            for a in al:
                # print(a)
                nums = re.findall('[0-9]+', a)
                a = re.sub(r'[0-9]+', '', a).replace(',', '')
                row = {'author': a, 'affli': ''}
                # print(nums)
                for n in nums:
                    for aff in afl:
                        if n in re.findall(r'[0-9]+', aff):
                            row['affli'] += re.sub(r'[0-9]+', '', aff) + '; '
                # print(row['affli'])
                det.append(row)
        else:
            for a in al:
                if len(a.split(' ')) <= 4:
                    det.append({'author': a, 'affli': afdet.replace('\n', '')})
        return det


    # Abstracts with pres number ER2.1 and ends with DOI:
    def get_abstracts(self, output):
        Absno = '^[A-Z]{1,4}[\d]+[\.]?[\d]?$'
        titlepat = '^[A-Z][\w\s\.,-?]+'
        abstlis = []
        abst = []
        lines = output.split('\n')
        i = 0
        while i < len(lines):
            if re.match(Absno, lines[i]) is not None:
                if i < len(lines) and len(lines[i + 1]) > 15 and self.validate_matches(titlepat, lines[i + 1]):
                    abstlis.append('\n'.join(abst))
                    abst = [lines[i]]
                else:
                    abst.append(lines[i])
            else:
                abst.append(lines[i])
            i += 1

        return abstlis

    # Any text processing operations:
    def process_text(self, text):
        # print('INSIDE PROCESS TXT')
        Doi = '^DOI: 10[\.]1530/[\w\.]+$'
        ptext = []
        for a in text.split('\n'):
            if self.validate_matches(Doi, a.strip()):
                ptext.append(a)
                break
            ptext.append(a)
        return '\n'.join(ptext)

    # process header and split to title and author blocks
    def process_header(self, head):
        lines = head.split('\n')
        if len(lines) == 4:
            res = {'absno': lines[0], 'title': lines[1].strip(), 'autdet': lines[2].strip(), 'affdet': lines[3].strip()}
            return res
        absno = lines[0]
        title = lines[1]
        # prev_line_length = len(lines[1])
        i = 2
        while i < len(lines):
            if self.validate_authorLine(lines[i].strip()): break
            else: title += ' '+lines[i]
            i += 1
        autafdet = '\n'.join(lines[i:])

        # if author block is not forund are empty
        if len(autafdet) == 0: raise Exception('Author Details Not found:\n'+title)

        aafblock = self.process_authorblock(autafdet)
        # print('AUTHOR splits:\n', aafblock)
        return {'absno': absno, 'title': title, 'autdet': aafblock[0], 'affdet': aafblock[1]}

    # process author block split author and affliations
    def process_authorblock(self,ablock):
        # if line starts with number then its a affliation
        # if a line contains and / &  then next line is affliation
        # else last two or one line is affiliation
        lines = ablock.split('\n')
        i = 0
        while i < len(lines):
            if self.validate_matches('^1[A-Z]', lines[i].strip()): break
            elif self.validate_matches('(.+ & .+)', lines[i].strip()):
                i += 1
                break
            elif self.validate_authorLine(lines[i]) is False: break
            i += 1
        if i < len(lines):
            details = [' '.join(lines[0:i]), ' '.join(lines[i:])]
        elif len(lines) < 3:
            details = [' '.join(lines[0:1]), ' '.join(lines[1:])]
        else:
            raise Exception('Unable To Parse Author Block')
        return details

    # To check author line
    def validate_authorLine(self, line):

        # if line start with numbers not an author
        if self.validate_matches('^[0-9]', line.strip()): return False

        # if lines contains three digit number not an author
        if self.validate_matches('[0-9]{3}', line.strip()): return False

        # if lines doesn't start with Capital letter then not an author
        if self.validate_matches('^[a-z].+', line.strip()): return False

        # remove all symbols(,`-.), and, & and check for cammel case
        line1 = line.replace('& ', '').replace('and ', '')
        pline = re.sub('[-`\.,0-9]', '', line1)
        # print('\nAUTHOR MATCH:', pline)
        # if there is a single word then not author
        if len(pline.split(' ')) < 2: return False

        count = 0
        for a in pline.split(' '):
            if a != '' and (self.validate_matches('[A-Z]', a.strip()[0]) is False):
                count += 1
        # if single author is present then Both the words should contains capital letters
        if len(pline.split(' ')) == 2 and count >0: return False
        if count > 1: return False
        return True


    # Define rules and check if abstract is valid
    def valid_abstract(self, item):
        # if contains Abstract Unavailable
        abs_unavail = re.compile('Abstract unavailable')
        if self.validate_matches(abs_unavail, item): raise Exception('Abstract is unavailable')

        # length should be greater than three.
        if len(item.split('\n')) < 4: raise Exception('Abstract length < 3')

    # to check regular expression passed as a string
    def validate_matches(self, regexp, item):
        rule = re.compile(regexp)
        if re.match(rule, item) is not None:
            return True
        else:
            return False

    # excel writer
    def write_to_excel(self, rows, columns, filename):
        df = pd.DataFrame(rows, columns=columns)
        # print(df.head())
        writer = ExcelWriter(filename)
        df.to_excel(writer, 'Sheet1')
        writer.save()


tp = TextProcessor()
file = 'ECTS2018.txt'
output_file = 'ECTS2018.xlsx'
error_file = 'errorECTS2018.xlsx'
text_file_data = ''
with open(file, encoding='utf-') as file:
    for line in file.readlines()[:]:
        text_file_data += line
# print(len(output))
records = tp.get_abstracts(text_file_data)
print('TOTAL ABSTRACTS :', len(records))
i = 1
output_rows = []
error_rows = []
# process each record
for abt in records:
    try:
        # check valid abstract
        tp.valid_abstract(abt)

        lines = abt.split('\n')
        head = '\n'.join(lines[0:3])

        # text seperator .\n
        temp = ('\n'.join(lines[3:])).split('.\n')
        if len(temp) < 2: raise Exception('Abstract is not valid: Affiliations missing')

        head += '\n'+temp[0]
        text = tp.process_text('\n'.join(temp[1:]))
        # print('HEAD:\n', i, head)
        # print('TEXT:\n', text)
        # break the header into title, autdet and affdet
        head_det = tp.process_header(head)
        print(head_det)
        # create entries for each author
        for a in tp.author_affli_matcher(head_det['autdet'],head_det['affdet']):
            row = {
                'text': '\n'.join(text.split('\n')[:-1]),
                'doi': text.split('\n')[-1],
                'absno': head_det['absno'],
                'title': head_det['title'],
                'author': a['author'],
                'affli': a['affli'],
            }
            output_rows.append(row)
    except Exception as e:
        error_rows.append({'reason': e, 'item': abt})
        print('ERROR MESSAGE', e)
        print(abt)
    i += 1

tp.write_to_excel(output_rows,['author', 'affli', 'title', 'absno', 'text', 'doi'], output_file)
tp.write_to_excel(error_rows,['reason', 'item'], error_file)

print('VALID SCRAPED ITEMS:', len(output_rows))
print('INVALID ABSTS:', len(error_rows))