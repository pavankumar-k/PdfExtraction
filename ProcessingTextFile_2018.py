# -*- coding: utf-8 -*-
"""
Created on Thu Jan 17 13:17:08 2019

@author: Vinutha
"""
import xlsxwriter

def GetName (name):
    Fname = ' '
    Mname = ' '
    Lname = ' '
    if name.find('.') !=-1:
        Fname = name.split('.')[0]
        Llist = name.split('.')[-1].split(' ')
        Lname = Llist[-1]

        if Fname == Lname:
            Lname=' '
        if len(Fname) != 0 and len (Lname) != 0:
            Mlist = name.split('.')
            Mlist.remove(Fname)
            n = '.'.join(i for i in Mlist)
            ln = n.split(' ')
            ln.remove(Lname)
            if len(ln) != 0:
                Mname = ' '+' '.join(i for i in ln)
     
    else:
        Fname = name.split(' ')[0]
        Lname = name.split(' ')[-1]
        if Fname == Lname:
            Lname = ''
        Mlist = name.split(' ')
        Mlist.remove(Fname)
        Mlist.remove(Lname)
        Mname = ' '.join(i for i in Mlist)
 
    return [Fname, Mname,Lname];

'''
##################################################################
'''



file = 'ESOC 2018.txt'
import re

ANo = re.compile('[A-Z]{2}\d+\-\d+')

record = []
with open(file, encoding='utf-') as file:
    item = ""
    Anum = ""
    Heading = ""
    Auth = ""
    for line in file.readlines()[:]:
#        print(line)

        if re.match(ANo, line) is not None:
#            with open('Ano.txt', 'a+') as file:
#                file.write(line)
            record.append([Anum,Auth,Heading, item])
            Anum = line.strip()
            item = ""
            Heading = ""
            Auth = ""
            
        elif re.search('[a-z]+',line) is None and item == "":
            Heading = Heading+line.replace('\n', ' ')
        
        elif item =="" and line.find('Background') ==-1:
            Auth = Auth+line.replace('\n', ' ')
            
            
        else: item = item+line

rows = []        
for item in record[1:]:
    Auth = re.split('[ |;]\d+', item[1])
#    print(Auth, len(Auth))
    
    for Doc in Auth[0].replace(' &', ',').split(', '):
#       print(Doc)
       try: pos = re.findall('\d+', Doc)[0]
       except: pos = '1'
       DocName = Doc.replace(pos, '')
       DocName = re.split(',|;', DocName)[0]
#       print(Doc, len(Auth), pos)
       try: DocAff = Auth[int(pos)]
       except: DocAff = ""
       
       try: Name = GetName(DocName)
       except: Name = ["","",""]
       rows.append(Name+[DocName, DocAff]+item)
       

FOutput = '4th European Stroke Organisation Conference (ESOC 2018).xlsx'
workbook = xlsxwriter.Workbook(FOutput, {'constant_memory': True})
worksheet = workbook.add_worksheet()

rw = 0
for row in rows:
    cl = 0
    for item in row:
#        item = item.replace('\t', ' ')
        item = item.replace('http', ' http')
        item = item.replace('\n',' ')
        worksheet.write(rw,cl,item)
        cl = cl+1
    rw +=1
workbook.close()
    