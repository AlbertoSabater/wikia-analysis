# -*- coding: utf-8 -*-

import numpy as np
import requests
from bs4 import BeautifulSoup
import bs4
import pickle
import re

BASE_URL = 'http://harrypotter.wikia.com'


def cleanString(s):
    s = s.strip()
    s = re.sub("\[\d+\]", "", s)
    return s

def get_content(parent, prefix=''):
    strs = []
    uls = parent.find_all('ul', recursive=False)
    
    if uls:
        # Read all lists
        for ul in uls:
            lis= ul.find_all('li', recursive=False)
            for li in lis:
                # Read all items in list
                if li.find('ul', recursive=False):
                    # If nested list, read it adding a prefix
                    aux = li.next
                    if not type(aux) == bs4.element.NavigableString:
                        aux = aux.get_text()
                    aux = cleanString(aux)
                    strs.append(prefix+aux)
                    strs += get_content(li, prefix=aux+' - ')
                else:
                    # If not nested list append content
                    strs.append(prefix+cleanString(li.get_text()))
    else:
        # Read not list content
        for v in parent.childGenerator():
            if type(v) == bs4.element.NavigableString:
                strs.append(prefix+cleanString(v))
            else:
                strs.append(prefix+cleanString(v.get_text()))
                
    strs = [ s for s in strs if re.search('\w', s) ]
                
    return strs


def read_profile(soup):
    # If not profile skip page
    profile = soup.find('aside', class_='portable-infobox')
    if not profile:
        return None
    items = profile.find_all('section', class_='pi-item')
    
    name = items[0].find('h2').get_text()
    
    character = {}
    character['name'] = name
    
    # Read character info per section
    for i in items[1:]:
        name_section = i.find('h2')
        if not name_section:
            continue
        name_section = name_section.get_text()
        sub_items = i.find_all('div', class_='pi-item')
        section = {}
        
        # Read subsection
        for si in sub_items:
            sub_name = si.find('h3').get_text()
            values = si.find_all('div', class_='pi-data-value')
            strs = []
            
            # Read values
            for val in values:
                strs += get_content(val)
            section[sub_name] = strs
        character[name_section] = section
        
    return character


# %%

# http://harrypotter.wikia.com/api/v1/Articles/List?expand=1&limit=1000&category=Females
# http://harrypotter.wikia.com/api/v1/Articles/AsSimpleJson?id=33353

categories = ['Females', 'Males']
results = []
i = 0
for cat in categories:
    url = 'http://harrypotter.wikia.com/api/v1/Articles/List?expand=1&limit=10000&category='+cat
    requested_url = requests.get(url)
    results += requested_url.json()['items']
    i += 1
    if i % 100 == 0:
        print i

cleaned = [ d for d in results if 'type' in d.keys() and d['type']=='article' ]


pages = []
for cl in cleaned:
    pages.append(requests.get(BASE_URL + cl['url']))


# %%
with open('pages_hp.pickle', 'w') as f:
    pickle.dump(pages, f)
    

# %%
with open('pages_hp.pickle', 'r') as f:
    pages = pickle.load(f)


# %%
characters = []
errors = []

# Iterate over all pages
for p in pages:
    # '/wiki/Severus_Snape'
    soup = BeautifulSoup(p.content, 'html.parser')
    
    print "Parsing:", p.request.url

    character = read_profile(soup)
    if not character:
        print 'ERROR:', p.request.url
        errors.append(p.request.url)
        continue
    character['url'] = p.request.url
    
    print "Character parsed:", character['name']
#    
#    characters += character
#    print '\n\n----------------------------------------'
#    print '----------------------------------------'
#    print '----------------------------------------\n\n'
#    
    
#    content = soup.find('div', class_='mw-content-text'.split())
    
    hs = soup.find_all('h2')
    appears = []
    for h in hs:
        if h.get_text() == 'Appearances':
            apps = h.find_next_siblings('ul')
            character['appears_raw'] = [ s for s in apps[0].get_text().split('\n') if s != '' ]
            apps = apps[0].find_all('a')
            for a in apps:
                appears.append(a.get_text())
            texts = apps[0].get_text()
            character['appears'] = appears
            break
            
            
                     
    characters.append(character)
      

# %%
with open('characters.pickle', 'w') as f:
    pickle.dump(characters, f)
    

# %%

if re.search('\w', u'   `´[a], '):
    print 'true'
else:
    print 'false'
    
    
# %%

d = [ d for d in characters if d['name']=='Severus Snape' ][0]
d = [ d for d in characters if d['name']=='Harry James Potter' ][0]
            