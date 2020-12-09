#import importlib
import matplotlib.pyplot as plt
#import cufflinks as cf
import hockey_bots as hockey
import datetime
import pandas as pd
import numpy as np

# players table (stats)
df_p = pd.read_csv("data/game_skater_stats.csv")
# game data dable
df_g = pd.read_csv("data/game.csv")
# player/goalie table (name, team, etc)
df_player = pd.read_csv("data/player_info.csv")
# shifts table
shifts = pd.read_csv("data/game_shifts.csv")
# teams
teams = pd.read_csv("data/team_info.csv")

#Test
select_Crosby = df_player.loc[df_player['lastName'] == 'Crosby']

############ Filtering Finding data for just 2018-2019 season ##########################
datetime.datetime.strptime
df = pd.read_csv('data/game_teams_stats.csv')
#Pick game_id, date_time and type (regular or playoff) from game_team_stats
df =  pd.merge(df, df_g[['game_id', 'date_time', 'type']])
#Sort on date_time
df['date_time'] = pd.to_datetime(df['date_time'])

df = df[(df['date_time'] > '2018-10-3') &
        (df['date_time'] < '2019-04-8') &
        (df['type'] == 'R')]
#sort team_id and date_time
df = df.sort_values(by=['team_id', 'date_time'])
#Add column game_number (82 games/season)
df['game_num'] = df.groupby('team_id').cumcount()

df_games = df[['game_id','team_id', 'won', 'game_num']]

#platyer stats for 2018-2019 season
df_p_2018 = hockey.player_merge(df_p, df_g, df_player)
df_p_2018 =df_p_2018[(df_p_2018['date_time'] > '2018-10-3') &
           (df_p_2018['date_time'] < '2019-04-8') &
           (df_p_2018['type'] == 'R')]

#Fantasy points
df_p_2018['points'] = df_p_2018.copy().apply(hockey.player_points, axis=1)
select_Crosby = df_p_2018.loc[df_p_2018['lastName'] == 'Crosby']

df_p_2018=df_p_2018.sort_values(by='date_time').reset_index(drop=True)
df_score = df_p_2018[['game_id', 'team_id', 'player_id','firstName', 'lastName', 'primaryPosition', 'points']]
a = pd.merge(df_score, df_games, on = 'game_id', how='left')
a=a.sort_values(by=['player_id', 'game_num'], ascending=False).drop_duplicates(subset=['player_id','game_num'])

##Compare proportion of points vs bin value for Edmonton and Tampa
#cf.set_config_file(offline=True)
#cf.datagen.lines(1, 500).ta_plot(study="sma", periods=[13, 21, 55])
#ax1 = pd.DataFrame()
#ax1['Edmonton Oilers'] = a[a.team_id_x==22]['points']

#ax2 = pd.DataFrame()
#ax2['Tampa Bay Lightning'] = a[a.team_id_x==14]['points']

#team_compare = pd.concat([ax1,ax2], ignore_index=True, axis=0, sort=False)
#team_compare.iplot(kind='hist',
#                   barmode='overlay',
#                   bins=25,
#                   histnorm='probability density',
#                   yTitle='Proportion of Points',
#                   xTitle = "Bin Value")

##If a player did not play a game then we fill his stats with zero points for that game
games = list(a.game_num.unique())
test = a.copy()
for player in a['player_id'].unique():
    games_played = list(a[a['player_id'] == player]['game_num'])
    fill_games = list(set(games) - set(games_played))
    for game in fill_games:
        pos = a[a['player_id'] == player]['primaryPosition'].to_list()[0]
        first = a[a['player_id'] == player]['firstName'].to_list()[0]
        last = a[a['player_id'] == player]['lastName'].to_list()[0]
        to_append = pd.DataFrame([[np.nan,
                                   np.nan,
                                   player,
                                   first,
                                   last,
                                   pos,
                                   0,
                                   np.nan,
                                   np.nan,
                                   game]],
                                 columns=list(a))
        test = test.append(to_append, ignore_index=True)

test.head()

#Ignore players that did not play more than 10 game 2018-2019 season
grouped = a.groupby('player_id').count()
players=list(grouped[grouped['won'] > 10].index)
test2=test[test['player_id'].isin(players)].reset_index(drop=True)
test2 = test2.fillna(0)
test2 = test2.sort_values(by=['player_id', 'game_num'])

p = a.groupby(['firstName', 'lastName']).count().sort_values(by='game_id', ascending=False).reset_index()
ax = p['game_id'].plot( figsize=(14,10), linewidth=3, grid=True)
ax.tick_params(axis="x", labelsize=16)
ax.tick_params(axis="y", labelsize=16)
ax.set_ylabel("Games Played", size = 22)
ax.set_xlabel("Player", size = 22)
plt.show()

#Save fixed player_data
test2.to_csv("fixed_data_2018.csv")

#Save fixed team data
a.to_csv("textaa.csv")