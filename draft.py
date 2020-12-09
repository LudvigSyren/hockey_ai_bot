#Run the draft

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

defence = hockey.position_indexes(pointies,all_points,player_data,idx, "D")
enter = hockey.position_indexes(pointies,all_points,player_data,idx, "C")
goalie = hockey.position_indexes(pointies,all_points, player_data,idx,"G")
right_wingers = hockey.position_indexes(pointies, all_points,player_data,idx,"RW")
left_wingers = hockey.position_indexes(pointies, all_points,player_data,idx,"LW")

#Retired players for the upcoming season

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

ret_names = ['Brooks Orpik', 'Matt Hendricks', "Roberto Luongo", 'Chrus Butler', 'Matt Cullen',
             'Chris Kunitz', 'Wade Megan', 'Stephen Gionta', 'Mike McKenna', 'Cam Ward',
             'Ben Lovejoy', 'Niklas Kronwall', 'Dan Giardi', 'Eric Gryba', 'Lee Stempniak',
             'Scott Eansor', 'Michael Leighton', 'Chris Thorburn', 'Dennis Seidenberg']

