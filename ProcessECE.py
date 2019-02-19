# -*- coding: utf-8 -*-
"""
Created on Thu Jan 17 09:23:31 2019

converted the pdf file to htlm using https://www.pdftohtml.net/ 

@author: Pavan
"""

#file = 'Poster Abstracts, 2017.html'
file2018 = 'ECE2018.html'

from bs4 import BeautifulSoup as BS
import pandas as pd
import re
import json

#def takeSecond(elem):
#    return elem[1]

'''
Get Position to split the data into left and right pane 
'''
def RSplit(items):
    pos = [ float(i['style'].split('left:')[-1].split('px')[0]) for i in items]
    df =pd.DataFrame(pos)
    g = df.groupby([0])[0].count()
    V = max(g.nlargest(2).index.tolist())
    return int(V)

ids = []
def getAbsList(lis):
    absl = []
    
    for a in lis:
        #print(a.text.strip())
        #input('Enter something:')
        ab = {}
        typ=''
        b = a.findAll('div',recursive=False)[2:-1]
        for i1 in range(2,len(b)-1):
            px = float(b[i1]['style'].split('left:')[-1].split('px')[0])
            px1 = 0
            if i1<len(b)-1:
                px1 = float(b[i1+1]['style'].split('left:')[-1].split('px')[0])
            #print(px)
            #input('test1')
            if px <400 and px1<400:
                typ = b[i1].text.strip()
                #print('inside if1',typ)
            elif px<400 :
                ab['type'] = typ
                ab['session'] = b[i1].text.strip()
                #print('inside if2',ab)
            elif px>400:
                t1 = (b[i1].text.strip()).replace(' ','')
                t = (re.sub(r'^(\.)+','',t1)).split('-')
                #print('PID:',t)
                
                if len(t)==1:
                    ab['id']=t[0]
                    absl.append(ab)
                    #print(ab)
                    ids.append(t[0])
                    ab={}
                else:
                    #input('Test2')
                    l=0
                    h=0
                    n1=0
                    tes = re.sub(r'((\.)|(\d))+','',t[0])
                    if len(re.findall(r'(\d\.\d)',t[0]))>0:
                        l = float(re.findall(r'(\d\.\d)',t[0])[0])
                        h = float(re.findall(r'(\d\.\d)',t[1])[0])
                        n1 = 0.1
                        tempabs = ab.copy()
                        tempabs['id'] = t[1].replace('.0','')
                        #print(tempabs)
                        absl.append(tempabs)
                        ids.append(tempabs['id'])
                    else:
                        l = float(re.findall(r'\d+',t[0])[0])
                        h = float(re.findall(r'\d+',t[1])[0])
                        n1 = 1
                    
                    #print('L:',l,'H:',h)
                    
                    while l<=h:
                        tempabs = ab.copy()
                        tempabs['id'] = tes+(re.findall(r'\d+\.\d',str(l))[0]).replace('.0','')

                        #print(tempabs)
                        absl.append(tempabs)
                        ids.append(tempabs['id'])
                        l+=n1
                    ab = {}
        
    return absl                         
                    
def getPreslist(pages):
    pl = []
    ab = []
    for page in pages[8:]:
        print(page.text.strip())
        input('enter')
        if page.text.strip() in ids:
            
            pl.append(ab)
            ab = [page]
        ab.append(page)
    return pl                         

html = open(file2018, encoding='utf-8').read()
soup = BS(html, 'lxml')
pages = soup.find('body').findAll('div', recursive=False)
print('STARTED PROCESSING')
absl = getAbsList(pages[3:8])
with open('output.jl','w') as file:
    for a in absl:
        file.write(json.dumps(a)+'\n')
    file.close()
#print(ids)
FullTxtLines = []
for page in pages[10:]:
    items = page.findAll('div', recursive=False)
    pos = RSplit(items)
#    print(pos)
    R=[]
    L=[]
    for item in items:
        p =float(item['style'].split('left:')[-1].split('px')[0])
        if p == 0: continue
    
        if p == pos or p>pos: R.append(item.text)
        else: L.append(item.text)

    
    FullTxtLines.extend(L+R)
    
with open('ECE2018.txt','a+' ,encoding='utf-8') as file:
    for txt in FullTxtLines:
        file.write(txt+'\n')







