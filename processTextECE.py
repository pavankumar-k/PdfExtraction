# -*- coding: utf-8 -*-
"""
Created on Thu Jan 17 13:17:08 2019
Pavan
"""
import re
#import xlsxwriter


#Author affiliation matcher
def authaffli(auth,affli):
    authlis = re.split(r'(, )|( & )|( and )',auth)
    aflis = affli.split(';')
    autflis = []
    for a in authlis:
        nums = re.findall(r'[0-9]+',a)
        if len(nums)>0:
            affli = ';'.join([aflis[int(x)-1].strip() for x in nums])
            auth = (re.sub(r'[0-9]+','',a)).replace(',','')
            autflis.append([auth,affli])
        else:
            autflis.append([auth,';'.join(aflis)])
    return autflis

#Author line identifier
def checkAuthorline(line):
    # replace all special characters other than letters,space and ,
    #print('GIVENAUTHORLINE',line)
    line = (re.sub(r'^[a-zA-Z/s]','',line)).replace(' and ',' ').strip()
    # if only one word exist not an author
    if len(line.split(' '))<2:return False
    count = 0
    #print(line.split(' '))
    #split with (, ) and check for the camel case in each word
    for a in line.split(' '):
        if re.match(r'[A-Z]',a.strip()[0]) is not None:
            count+=1
    #print(count)
    #if most of the letters have camel case it is author line else not an author line
    if count == len(line.split(' ')) or count== len(line.split(' '))-1:return True
    else: return False

# header processor
def getheadfields(headlines):

    det = []
    if len(headlines)==3:
        title = ''
        #if there are threee lines use as title, auth and affli
        title = headlines[0].strip()
        auth = headlines[1].strip()
        affli = headlines[2].strip()
        for a in authaffli(auth,affli):
            det.append({'author':a[0],'title':title,'affli':a[1]})
    else:
        title = ''
        authaflis = []
        authdet = ''
        n=0
        while n<len(headlines):
            if checkAuthorline(headlines[n]) == True:break
            n+=1
        title = ' '.join([x.strip() for x in headlines[0:n]])
        authdet = '\n'.join([x.strip() for x in headlines[n:]])
        print('Title', title)
        if authdet == '': raise Exception('author details is not found:\n'+title)

        # auth det contains numbers check from last line and if 1 occurs at start of the line - lines above are authors
        if re.match(r'[0-9]+',authdet.split('\n')[0]) is not None:
            lines = authdet.split('\n')
            i = len(lines)-1
            while i>=0:
                if lines[i].match(r'^1[A-z]') is not None:break
                i-=1
            authaflis = authaffli(' '.join(lines[0:i]),' '.join(lines[i:]))
            print('Inside num type')
        elif re.match(r', ',authdet.split('\n')[0]) is not None:
            lines = authdet.split('\n')
            i = 0
            while i<len(lines):
                if lines[i].match(r'( & )|( and )') is not None:break
                i+=1
            authaflis = authaffli(' '.join(lines[0:i+1]),' '.join(lines[i+1:]))
            print('Inside commas')
        else:
            lines = authdet.split('\n')
            authaflis = [[lines[0].strip(),' '.join(lines[1:])]]

        for a in authaflis:
            det.append({'author': a[0], 'title': title, 'affli': a[1]})
    return det



'''
###################### Text Processor ##############################
'''

file = 'ECE2018.txt'
import re
#to match just before the ABS number
ANo = re.compile('^(?=[A-Z]{1,4}[\d]+[\.]{0,1}[\d]{0,1}$)')
AbsEndLine = re.compile('\nDOI: 10[\.]1530/[\w\.]+\n')

records = []
output = ''
with open(file, encoding='utf-') as file:
    for line in file.readlines()[:]:
        output+=line
#split just before abs number
records = re.split(r'[\n]+[A-Z]{1,4}[\d]+[\.]{0,1}[\d]{0,1}[\n]+',output)
#print(output.split('\n')[0])
print(len(records))
#print(records[1])
input('Test for the ANO:')
rows = []
for item in records[1:]:
    try:
        print(item)
        #Affiliations are ended by .\n
        lines = re.split('\.[\n]+',item)
        head = lines[0]
        body = '.\n'.join(lines[1:])
        text = ''
        doi = ''
        # processing body of abstract by cutting upto DOI
        for line in re.split('\n+',body):
            if re.match(AbsEndLine,line) is not None:
                doi = line
                break
            else:
                text+=line.strip()
        #print('DOI',doi)
        #print('TEXT:\n',text)
        #input('TEST TEXT VERIFIER')
        # get title author and affiliation fields(as list of dicts)
        headlines = re.split('\n+',head)
        print(head)
        #input('Test Lines')
        for a in getheadfields(headlines[0:]):
            row=[a['author'],a['affli'],a['title'],text,doi]
            print(row)
            input('Test for each author and affli:')
            rows.append(row)
    except Exception as e:
        print('UNABLE TO PARSE THE TEXT :', e)
    #    with open('error.txt','a',encoding='utf-8') as file:
    #        file.write(item)
    #        file.close()
    input('NEXT ITEM')
'''
############################### Excel Writer #####################################
FOutput = 'ECE2018.xlsx'
workbook = xlsxwriter.Workbook(FOutput, {'constant_memory': True})
worksheet = workbook.add_worksheet()

rw = 0
for row in rows:
    cl = 0
    for item in row:
        #        item = item.replace('\t', ' ')
        item = item.replace('http', ' http')
        item = item.replace('\n', ' ')
        worksheet.write(rw, cl, item)
        cl = cl + 1
    rw += 1
workbook.close()
'''