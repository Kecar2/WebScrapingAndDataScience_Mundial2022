#!/usr/bin/env python
# coding: utf-8

# In[13]:


from bs4 import BeautifulSoup
import requests
import pandas as pd


# In[14]:


web = 'https://en.wikipedia.org/wiki/2014_FIFA_World_Cup'
response = requests.get(web)
content = response.text
soup = BeautifulSoup(content, 'lxml')

matches = soup.find_all('div', class_='footballbox')

home = []
score = []
away = []

for match in matches:
    home.append(match.find('th', class_='fhome').get_text())
    score.append(match.find('th', class_='fscore').get_text())
    away.append(match.find('th', class_='faway').get_text())


# In[16]:


dict_football = {'home': home, 'score': score, 'away': away}


# In[18]:


df_football = pd.DataFrame(dict_football)
df_football['year'] = '2014'


# In[19]:


print(df_football)


# In[24]:


years = [1930, 1934, 1938, 1950, 1954, 1958, 1962, 1966, 1970, 1974, 1978, 1982, 1986, 1990, 1994, 2002, 2006, 2010, 2014, 2018]


# In[22]:


def get_matches(year):
    web = f'https://en.wikipedia.org/wiki/{year}_FIFA_World_Cup'
    response = requests.get(web)
    content = response.text
    soup = BeautifulSoup(content, 'lxml')

    matches = soup.find_all('div', class_='footballbox')

    home = []
    score = []
    away = []

    for match in matches:
        home.append(match.find('th', class_='fhome').get_text())
        score.append(match.find('th', class_='fscore').get_text())
        away.append(match.find('th', class_='faway').get_text())
    
    dict_football = {'home': home, 'score': score, 'away': away}
    
    df_football = pd.DataFrame(dict_football)
    df_football['year'] = year
    return df_football


# In[23]:


print(get_matches(1982))


# In[26]:


fifa = [get_matches(year) for year in years]


# In[29]:


df_fifa = pd.concat(fifa, ignore_index=True)
df_fifa.to_csv('fifa_worldcup_historial_data.csv', index=False)


# In[30]:


df_fixture = get_matches('2022')
df_fixture.to_csv('fifa_worldcup_fixture.csv', index=False)

