# python 3.7
import re
import os
import shutil
import xml.etree.ElementTree as ET
from textrank4zh import TextRank4Keyword, TextRank4Sentence
import random

NEWS_Pool = []

targetdir = '../data/news/sorted/'

if os.path.exists(targetdir):
    shutil.rmtree(targetdir)
os.mkdir(targetdir)

neteasefiles = os.listdir('../data/news/netease/')

print("Netease : " + str(len(neteasefiles)))

filelist = []

for newsfile in neteasefiles:
    filelist.append('../data/news/netease/'+newsfile)

print("Sum number : " + str(len(filelist)))

random.shuffle(filelist)

tr4w = TextRank4Keyword()

count = 0

for file in filelist:
    try:
        root = ET.parse(file).getroot()
    except:
        print("Read XML Failed.")
        continue
    title = root.find('title').text
    body = root.find('body').text
    docid = int(count)
    date_time = root.find('datetime').text
    url = root.find('url').text
    NEWS_Pool.append(url)
    if body is None or title is None:
        print("Body or Title None Error.")
        continue
    try:
        keywords = []
        body.replace("\n","")
        body.replace("\t"," ")
        if 'var' in body:
            print("HTML Structure Uncleaned.")
            rule = re.compile("[^\，\。\！\u4e00-\u9fa5]")
            body = rule.sub('',body)
            #print(body)
        body_cleaned = re.sub("[\[\`\~\@\#\$\^\&\*\'\'\%]", "", body)
        title_cleaned = re.sub("[\[\`\~\@\#\$\^\&\*\'\'\%]", "", title)
        tr4w.analyze(text=body_cleaned, lower=True, window=2)
        for item in tr4w.get_keywords(10, word_min_len=2):
            keywords.append(item.word+" "+str(item.weight))
        tr4s = TextRank4Sentence()
        try:
            tr4s.analyze(text=body_cleaned, lower=True, source = 'all_filters')
            item = tr4s.get_key_sentences(num=1)[0]
            selected_snippet = item.sentence
        except Exception as e:
            print("TextRank4Sentence error : " + str(e))
            if len(body) > 50:
                selected_snippet = body[0:50]#article.cleaned_text[0:150]
            else:
                selected_snippet = body
        if len(body) > 150:
            naive_snippet = body[0:150]#article.cleaned_text[0:150]
        else:
            naive_snippet = body
    except Exception as e:
        print("TextRank error : " + str(e))
        continue
    try:
        doc = ET.Element("doc")
        ET.SubElement(doc, "id").text = str(docid)
        ET.SubElement(doc, "url").text = url
        ET.SubElement(doc, "title").text = title_cleaned
        ET.SubElement(doc, "datetime").text = date_time+":00"
        ET.SubElement(doc, "body").text = body_cleaned
        ET.SubElement(doc, "keywords").text = ";".join(keywords)
        ET.SubElement(doc, "naive_snippet").text = naive_snippet
        ET.SubElement(doc, "selected_snippet").text = selected_snippet

        tree = ET.ElementTree(doc)
        tree.write(targetdir + str(docid) + ".xml", encoding = 'utf-8', xml_declaration = True)
    except:
        print("To XML Failed.")
        continue
    count += 1
    print(str(count) + " th. done.")

    if count == 10000:
        break
