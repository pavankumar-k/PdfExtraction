# -*- coding: utf-8 -*-
"""
Created on Thu Jan 17 13:17:08 2019
Pavan
"""
import re
import xlsxwriter


#Author affiliation matcher
def authaffli(auth,affli):
    authlis = re.split(r'(, )|( & )|( and )')
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
    line = (re.sub(r'[a-zA-z/s]','',line)).replace(' and ',' ')
    # if only one word exist not an author
    if len(line.split(' '))<2:return False
    count = 0
    #split with (, ) and check for the camel case in each word
    for a in line.split(', '):
        if re.match(r'^[A-Z]]') is not None:
            count+=1
    #if most of the letters have camel case it is author line else not an author line
    if count == len(line.split(', ')) or count== len(line.split(', '))-1:return True
    else: return False

# header processor
def getheadfields(headlines):

    det = []
    if len(headlines)==3:
        title = ''
        #if there are threee lines use as title, auth and affli
        title = headlines[0].strip()
        auth = headlines[1].strip().split()
        affli = headlines[2].strip()
        for a in authaffli(auth,affli):
            det.append({'author':a[0],'title':title,'affli':a[1]})
    else:
        title = ''
        authaflis = []
        authdet = ''
        for line in headlines:
            if title!='' and checkAuthorline == True:
                authdet+=line+'\n'
            else:
                title+=line.strip()
        if authdet == '': raise Exception('author details is not found:\n'+title)
        # auth det contains numbers check from last line and if 1 occurs at start of the line - lines above are authors
        if re.match(r'[0-9]+',authdet.split('\n')[0]) is not None:
            lines = authdet.split('\n')
            i = len(lines)-1
            while i>=0:
                if lines[i].match(r'^1[A-z]') is not None:break
                i-=1
            authaflis = authaffli(' '.join(lines[0:i]),' '.join(lines[i:]))
        elif re.match(r', ',authdet.split('\n')[0]) is not None:
            lines = authdet.split('\n')
            i = 0
            while i<len(lines):
                if lines[i].match(r'( & )|( and )') is not None:break
                i+=1
            authaflis = authaffli(' '.join(lines[0:i+1]),' '.join(lines[i+1:]))
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
AbsEndLine = re.compile('^DOI: 10[\.]1530/[\w\.]+$')

records = []
output = ''
with open(file, encoding='utf-') as file:
    for line in file.readlines()[:]:
        output+=line
#split just before abs number
records = re.split(r'^(?=[A-Z]{1,4}[\d]+[\.]{0,1}[\d]{0,1}$)',output)
print(len(records))
print(records[1])
input('Test for the ANO:')
rows = []
for item in records[1:]:
    try:
        #Affiliations are ended by .\n
        lines = item.split('.\n')
        head = lines[0]
        body = '.\n'.join(lines[1:])
        text = ''
        doi = ''
        # processing body of abstract by cutting upto DOI
        for line in body.split('\n'):
            if line.match(r'^DOI: 10[\.]1530/[\w\.]+$') is not None:
                doi = line
                break
            else:
                text+=line.strip()
        print('DOI',doi)
        print('TEXT:\n',text)
        input('TEST TEXT VERIFIER')
        # get title author and affiliation fields(as list of dicts)
        headlines = head.split('\n')
        absnum = headlines[0].strip()
        for a in getheadfields(headlines[1:]):
            row=[a['author'],a['affli'],a['title'],absnum,text,doi]
            print(row)
            input('Test for each author and affli:')
            rows.append(row)
    except Exception as e:
        print('UNABLE TO PARSE THE TEXT :', e)
        with open('error.txt','a') as file:
            file.write(item)
            file.close()

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
