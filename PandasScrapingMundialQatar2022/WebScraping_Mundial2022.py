#!/usr/bin/env python
# coding: utf-8

# In[32]:


import pandas as pd
from string import ascii_uppercase as alf
import pickle


# In[2]:


tablas = pd.read_html('https://en.wikipedia.org/wiki/2022_FIFA_World_Cup')


# In[12]:


# A -> H
# 11 -> 7*8 +11 = 67
tablas[12]
tablas[19]


# In[27]:


alf


# In[22]:


tablas[19].columns[1]


# In[29]:


tablas = pd.read_html('https://en.wikipedia.org/wiki/2022_FIFA_World_Cup')

dict_tablas = {}
for letter, i in zip(alf, range(12, 68, 7)):
    df = tablas[i]
    df.rename(columns={df.columns[1]: 'Team'}, inplace=True)
    df.pop('Qualification')
    dict_tablas[f'Grupo {letter}'] = df


# In[30]:


dict_tablas.keys()


# In[31]:


dict_tablas['Grupo A']


# In[33]:


with open('dic_table', 'wb') as output:
    pickle.dump(dict_tablas, output)

