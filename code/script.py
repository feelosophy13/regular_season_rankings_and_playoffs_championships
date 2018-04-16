## Do teams with the highest regular-season win percentages win championships?
## Which regular season rankings best predict the playoffs champions?


## import libraries
import numpy as np
import pandas as pd
import nba_py
from nba_py import team, game, player, constants


## get a df of team ids
team_list_df = nba_py.team.TeamList(league_id='00').info().dropna()
team_list_df


## get a list of team ids
team_ids = [nba_py.constants.TEAMS[key]['id'] for key in nba_py.constants.TEAMS]



#### get playoff champions and conference winners by season

## initialize df
conf_win_df = champ_df = pd.DataFrame()

## add to df
for team_id in team_ids:
    
    team_details = nba_py.team.TeamDetails(team_id=team_id)
    
    ## for conference winner info
    df = team_details.awards_conf()
    df['TEAM_ID'] = team_id
    conf_win_df = conf_win_df.append(df)
    
    ## for playoffs champion info
    df = team_details.awards_championships()
    df['TEAM_ID'] = team_id
    champ_df = champ_df.append(df)

## clean conference winner df
conf_win_df['SEASON'] = conf_win_df['YEARAWARDED'].apply(lambda x: str(x - 1) + "-" + str(x)[2:])
conf_win_df['CONF_CHAMP'] = True
conf_win_df = conf_win_df.drop(['OPPOSITETEAM', 'YEARAWARDED'], 1)

## clean playoff champion df
champ_df['SEASON'] = champ_df['YEARAWARDED'].apply(lambda x: str(x - 1) + "-" + str(x)[2:])
champ_df['PLAYOFFS_CHAMP'] = True
champ_df = champ_df.drop(['OPPOSITETEAM', 'YEARAWARDED'], 1)

## merge conference and playoff winner dfs
fin_win_df = pd.merge(conf_win_df, champ_df, how='left', on=['TEAM_ID', 'SEASON'])
fin_win_df = fin_win_df.sort_values(['SEASON', 'TEAM_ID'])
fin_win_df['PLAYOFFS_CHAMP'] = fin_win_df['PLAYOFFS_CHAMP'].fillna(False)
fin_win_df['TEAM_ID'] = fin_win_df['TEAM_ID'].astype(str)


## get all relevant seasons
# seasons = list(sorted(set(x['SEASON'])))



#### get teams' summary info by season
team_summary_df = pd.DataFrame()
for team_id in team_ids:
    df = nba_py.team.TeamSummary(team_id=team_id).info()
    team_summary_df = team_summary_df.append(df)
team_summary_df = team_summary_df[['TEAM_ID', 'TEAM_CONFERENCE']]
team_summary_df['TEAM_ID'] = team_summary_df['TEAM_ID'].astype(str)



#### get teams' year-over-year info
team_yoy_df = pd.DataFrame()
for team_id in team_ids:
    df = nba_py.team.TeamYearOverYearSplits(team_id=team_id).by_year()
    df['TEAM_ID'] = team_id
    team_yoy_df = team_yoy_df.append(df)
select_cols = ['GROUP_VALUE', 'TEAM_ID'] + list(team_yoy_df.filter(like='RANK').columns)
team_yoy_df = team_yoy_df[select_cols].drop(['GP_RANK', 'W_RANK', 'L_RANK', 'MIN_RANK'], 1)
team_yoy_df = team_yoy_df.rename(columns={'GROUP_VALUE': 'SEASON'})
team_yoy_df['TEAM_ID'] = team_yoy_df['TEAM_ID'].astype(str)



#### get a final df to use for analysis by merging
df = pd.merge(left=team_yoy_df, right=fin_win_df, how='left', on=['TEAM_ID', 'SEASON'])
df = pd.merge(left=df, right=team_summary_df, how='left', on='TEAM_ID')
df[['CONF_CHAMP', 'PLAYOFFS_CHAMP']] = df[['CONF_CHAMP', 'PLAYOFFS_CHAMP']].fillna(False)



#### measure playoff champ predictive power for each rank metric
rank_cols = list(df.filter(like='RANK').columns)
summary_df = pd.DataFrame()
for col in rank_cols:
    dict = {
        'rank': [col],
        'n': [df.loc[x[col] == 1, 'PLAYOFFS_CHAMP'].sum()]    
    }
    new_row_df = pd.DataFrame(dict)
    summary_df = summary_df.append(new_row_df)
summary_df = summary_df.sort_values(by='n', ascending=False)
summary_df = summary_df[['rank', 'n']]
summary_df.to_html('filename.html')


