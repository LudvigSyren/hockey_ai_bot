#Run the draft
import json
import pickle
import numpy as np
import pandas as pd
import cvxpy as cp
import hockey_bots as hockey

#Import fixed player data from collect_data
player_data = pd.read_csv("fixed_data_2018.csv")


#Not sure about what next_year is used for yet but here it contains the same data as player_data
next_year = pd.read_csv("fixed_data_2018.csv")
# aggregate all scores into an array for each player
scores = player_data[['player_id', 'points',]].groupby('player_id').agg(lambda x: list(x)).reset_index()
player_pos = player_data[['player_id', 'primaryPosition']]
unique_pos = []
#count of each player at resp pos.
for id in player_pos.player_id.unique():
    temp_pos = player_pos.loc[player_pos['player_id'] == id]['primaryPosition'].reset_index(drop=True)
    unique_pos.append(temp_pos[0])
#player_pos = player_pos.loc[player_pos['player_id'] == player_pos.player_id.unique()]
df_unique_pos = pd.DataFrame(unique_pos, columns=['pos'])
print(df_unique_pos['pos'].value_counts())
scores_next = next_year[['player_id', 'points',]].groupby('player_id').agg(lambda x: list(x)).reset_index()

#This is not clear to me
scores_next = scores_next[scores_next.player_id.isin(scores.player_id.unique())]
scores = scores[scores.player_id.isin(scores_next.player_id)].reset_index(drop = True)
scores_next = scores_next.set_index(scores.player_id).reset_index(drop=True)
player_data = player_data[player_data.player_id.isin(scores.player_id)]
#
all_points = pd.DataFrame(np.transpose(scores.points.tolist()), columns = scores.player_id)
all_points_next = pd.DataFrame(np.transpose(scores_next.points.tolist()), columns = scores_next.player_id)
idx = list(all_points.mean().sort_values(ascending=False).index)

#Weighting of data, not really sure why
all_points = (all_points - all_points.min().max())/(all_points.max().max() - all_points.min().min())

# Finding index in an aggregate score for each position
pointies = list(all_points.mean().index)

#Pick out players in resp position
defence = hockey.position_indexes(pointies,all_points,player_data,idx, "D")
center = hockey.position_indexes(pointies,all_points,player_data,idx, "C")
#goalie = hockey.position_indexes(pointies,all_points, player_data,idx,"G")
right_wingers = hockey.position_indexes(pointies, all_points,player_data,idx,"RW")
left_wingers = hockey.position_indexes(pointies, all_points,player_data,idx,"LW")
#Looks like some players are missing after this operation

#Exclude player that has retired for the upconing season
def exclude_retired(players, names):
    retired = []
    for name in names:
        first, last = name.split(" ")

        df = players[(players.firstName.str.contains(first, case=False)) &
                     (players.lastName.str.contains(last, case=False))]

        try:
            p = df['player_id'].unique()[0]
            df2 = all_points.mean().reset_index()
            player_index = list(df2[df2['player_id'] == p].index)[0]
            retired.append(player_index)
        except:
            print(name, "is bad")

    return retired

def create_teams(team_names):
    teams = {

    }
    for team_name in team_names:
        teams[team_name]

ret_names = ['Brooks Orpik', 'Matt Hendricks', "Roberto Luongo", 'Chrus Butler', 'Matt Cullen',
             'Chris Kunitz', 'Wade Megan', 'Stephen Gionta', 'Mike McKenna', 'Cam Ward',
             'Ben Lovejoy', 'Niklas Kronwall', 'Dan Giardi', 'Eric Gryba', 'Lee Stempniak',
             'Scott Eansor', 'Michael Leighton', 'Chris Thorburn', 'Dennis Seidenberg']

##Run draft
functions = [hockey.optim_player,
             hockey.optim_player,
             hockey.optim_player,
             hockey.optim_player,
            hockey.optim_player,
            hockey.optim_player,
            hockey.optim_player,
            hockey.optim_player]

greedy_selections = {}
greedy_selections['defence'] = []
greedy_selections['center'] = []
greedy_selections['right_winger'] = []
greedy_selections['left_winger'] = []


order = [3,0,6,7,2,4,5,1]

print(len(order), len(functions))

team_names =["FIGHTING SQUIRRELS", "SNORKY SPEAK MAN", "SAD SKATERS",
            "BURNING ICE", "DESTRUCTUS", "FROZEN HOPE",
            "BYRON", "BIG G"]
team_names = [x.upper() for x in team_names]
print(team_names)
args = dict(scores = all_points,
            gammaa = [0.01, 0.01, 0.03, 0.8, 0, 0.89, 0.5, 0.6],
            greedy_selections = greedy_selections,
            df = player_data,
            defence = defence,
            center = center,
            left_wingers = left_wingers,
            right_wingers = right_wingers,
            selection = ['max', 'optim', 'optim', 'max', 'max', 'optim', 'max', 'optim'],
            sub_gamma = [None, 0.3, 0.8, None, None, .02, None, 0.4])

taken = exclude_retired(player_data, ret_names)
print(taken)
fantasy_teams = {
    "FIGHTING SQUIRRELS" : [],
    "SNORKY SPEAK MAN" : [],
    "SAD SKATERS" : [],
    "BURNING ICE" : [],
    "DESTRUCTUS" : [],
    "FROZEN HOPE" : [],
    "BYRON" : [],
    "BIG G" : []}
all_players, teams, fantasy_teams = hockey.draft(functions, order, pause= False, team_names = team_names, team_size=14, fantasy_teams = fantasy_teams,**args)
#Save to fantasy_teams to json-file
fantasy_json = json.dumps(fantasy_teams)
jsonhandler = open("fantasy_teams_1.json", "w")
jsonhandler.write(fantasy_json)
jsonhandler.close()
#Save with pickle

picklehandler = open("fantasy_teams_pickle_1", "wb")
pickle.dump(fantasy_teams, picklehandler)
picklehandler.close()


