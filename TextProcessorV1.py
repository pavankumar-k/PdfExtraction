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

    # Define rules and check if abstract is valid
    def valid_abstract(self, item):
        # if contains Abstract Unavailable
        abs_unavail = 'Abstract unavailable'
        if self.validate_matches(abs_unavail, item): raise Exception('Abstract is unavailable')

        # length should be greater than three.
        if len(item.split('\n')) < 3: raise Exception('Abstract length < 3')

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
        absno = lines[0].strip()
        title = lines[1].strip()
        i = 2
        while i < len(lines):
            if tp.validate_authorline(lines[i]): break
            else: title += ' '+lines[i]
            i += 1
        authorlis = ''
        while i < len(lines):
            if tp.validate_authorline(lines[i]): authorlis += lines[i].strip()+' '
            else: break
            i += 1
        afflis = ''
        while i < len(lines):
            if tp.validate_affilitation(lines[i]): afflis += lines[i].strip()+' '
            else: break
            i += 1
        text = '\n'.join(lines[i:])

    except Exception as e:
        error_rows.append({'reason': e, 'item': abt})
        print('ERROR MESSAGE', e)
        print(abt)
    i += 1

tp.write_to_excel(output_rows,['author', 'affli', 'title', 'absno', 'text', 'doi'], output_file)
tp.write_to_excel(error_rows,['reason', 'item'], error_file)

print('VALID SCRAPED ITEMS:', len(output_rows))
print('INVALID ABSTS:', len(error_rows))