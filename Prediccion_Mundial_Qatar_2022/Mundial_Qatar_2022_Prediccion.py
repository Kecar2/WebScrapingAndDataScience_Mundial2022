#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import pickle
from scipy.stats import poisson


# In[2]:


dict_table = pickle.load(open('dict_table', 'rb'))
df_historical_data = pd.read_csv('clean_fifa_worldcup_matches.csv')
df_fixture = pd.read_csv('clean_fifa_worldcup_fixture.csv')


# # 1 Calcular Team Strength

# In[3]:


df_historical_data


# In[4]:


# Dividir df en df_home and df_away
df_home = df_historical_data[['HomeTeam', 'HomeGoals', 'AwayGoals']]
df_away = df_historical_data[['AwayTeam', 'HomeGoals', 'AwayGoals']]


# In[5]:


df_away, df_home


# In[6]:


# renombrar columnas
df_home = df_home.rename(columns={'HomeTeam': 'Team', 'HomeGoals': 'GoalsScored', 'AwayGoals': 'GoalsConceded'})
df_away = df_away.rename(columns={'AwayTeam': 'Team', 'HomeGoals': 'GoalsConceded', 'AwayGoals': 'GoalsScored'})


# In[7]:


df_home, df_away


# In[8]:


# concatenar df_home y df_away, hacer group por team y calcular promedio
df_team_strength = pd.concat([df_home, df_away], ignore_index=True).groupby('Team').mean()


# In[9]:


df_team_strength


# # 2 Funcion predict_points

# ## Distribución Poisson
# 
# ### - La distribución de Poisson es una distribución discreta que describe el número de eventos que ocurren en un intervalo de tiempo fijo o región de opurtunidad.
# 
# #### - Goal: Evento que puede ocurrir en los 90 minutos de un partido de fútbol
# 
# ### - Condiciones: 
# #### 1. El número de eventos se puede contar
# #### 2. La ocurrencia de eventos son independientes
# #### 3. La tasa a la que ocurren los eventos es constante.
# #### 4. Dos eventos no pueden ocurrir exactamente en el mismo instante de tiempo

# In[10]:


def predict_points(home, away):
    if home in df_team_strength.index and away in df_team_strength.index:
        # goals_scored * goals_conceded
        lamb_home = df_team_strength.at[home,'GoalsScored'] * df_team_strength.at[away,'GoalsConceded']
        lamb_away = df_team_strength.at[away,'GoalsScored'] * df_team_strength.at[home,'GoalsConceded']
        prob_home, prob_away, prob_draw = 0, 0, 0
        for x in range(0, 11): #number of goals home team
            for y in range(0, 11): #number of goals away team
                p = poisson.pmf(x, lamb_home) * poisson.pmf(y, lamb_away)
                if x == y:
                    prob_draw += p
                elif x > y:
                    prob_home += p
                else:
                    prob_away += p
        
        points_home = 3 * prob_home + prob_draw
        points_away = 3 * prob_away + prob_draw
        return (points_home, points_away)
    else:
        return (0, 0)


# # 2.1 Test Funcion

# In[11]:


# Testear con partidos Argentina - Mexico, England - USA, Qatar (H) - Ecuador
# predict_points('Argentina', 'Mexico')
predict_points('England', 'United States')
# predict_points('Qatar (H)', 'Ecuador')


# # 3.1 Fase de grupo

# In[14]:


# dividiendo fixture en grupo, octavos, cuartos, semi, final.
df_fixture_group_48 = df_fixture[:48].copy()
df_fixture_knockout = df_fixture[48:56].copy()
df_fixture_quarter = df_fixture[56:60].copy()
df_fixture_semi = df_fixture[60:62].copy()
df_fixture_final = df_fixture[62:].copy()


# In[16]:


# Correr todos los partidos de la fase de grupo y actualizar las tablas de cada grupo
for group in dict_table:
    teams_in_group = dict_table[group]['Team'].values
    df_fixture_group_6 = df_fixture_group_48[df_fixture_group_48['home'].isin(teams_in_group)]
    for index, row in df_fixture_group_6.iterrows():
        home, away = row['home'], row['away']
        points_home, points_away = predict_points(home, away)
        dict_table[group].loc[dict_table[group]['Team'] == home, 'Pts'] += points_home
        dict_table[group].loc[dict_table[group]['Team'] == away, 'Pts'] += points_away
    
    dict_table[group] = dict_table[group].sort_values('Pts', ascending=False).reset_index()
    dict_table[group] = dict_table[group][['Team', 'Pts']]
    dict_table[group] = dict_table[group].round(0)


# In[18]:


# Mostrar tabla actualizada
dict_table['Group B']


# # 3.2 Octavos

# In[19]:


# Octavos: df_fixture_knockout
df_fixture_knockout


# In[20]:


dict_table.keys()


# In[21]:


# Actualizar el fixture de octavos con el 1 puesto (group winner) y 2 puesto (runners up)
for group in dict_table:
    group_winner =  dict_table[group].loc[0, 'Team']
    group_runners_up = dict_table[group].loc[1, 'Team']
    df_fixture_knockout.replace({f'Winners {group}': group_winner,
                                f'Runners-up {group}': group_runners_up}, inplace=True)
    
df_fixture_knockout['winner'] = '?'
df_fixture_knockout


# In[22]:


# Crear funcion get_winner
def get_winner(df_fixture_updated):
    for index, row in df_fixture_updated.iterrows():
        home, away = row['home'], row['away']
        points_home, points_away = predict_points(home, away)
        if points_home > points_away:
            winner = home
        else:
            winner = away
        df_fixture_updated.loc[index, 'winner'] = winner
    return df_fixture_updated


# In[26]:


get_winner(df_fixture_knockout)


# # 3.3 Cuartos de Final

# In[32]:


# Crear update_table fuction
def update_table(df_fixture_round_1, df_fixture_round_2):
    for index, row in df_fixture_round_1.iterrows():
        winner = df_fixture_round_1.loc[index, 'winner']
        match = df_fixture_round_1.loc[index, 'score']
        df_fixture_round_2.replace({f'Winners {match}':winner}, inplace=True)
    df_fixture_round_2['winner'] = '?'
    return df_fixture_round_2


# In[35]:


update_table(df_fixture_knockout, df_fixture_quarter)


# In[36]:


get_winner(df_fixture_quarter)


# # 3.4 Semifinal

# In[37]:


update_table(df_fixture_quarter, df_fixture_semi)


# In[38]:


get_winner(df_fixture_semi)


# # 3.5 Final

# In[39]:


update_table(df_fixture_semi, df_fixture_final)


# In[40]:


get_winner(df_fixture_final)


# In[ ]:




