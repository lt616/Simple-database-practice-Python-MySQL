# COMP4111 Assignment 01 - top 10 hitter for RDB implementation 
# Author: Qianrui Zhao      ID: qz2338 
# Any question please contact qz2338@columbia.edu 

from RDBTable import RDBTable 
import sys 


connect_info = {} 
connect_info["localhost"] = "localhost" 
connect_info["dbuser"] = "COMS4111_user" 
connect_info["password"] = "qz2338" 
connect_info["dbname"] = "COMS4111_assignment01" 

primary_keys = ["playerID", "birthMonth", "birthDay"]

db_people = RDBTable("People", "People.csv", primary_keys, connect_info)
db_people.load() 

primary_keys = ["playerID", "yearID", "teamID", "stint"]
db_batting = RDBTable("Batting", "Batting.csv", primary_keys, connect_info)
db_batting.load() 

all_players_info = db_people.find_by_template({}, ["playerID", "nameFirst", "nameLast"]) 
all_scores = {} 
all_players_result = {} 

all_battles = db_batting.find_by_template({}, ["playerID", "yearID", "AB", "H"]) 
battles_info_dict = {} 

for info in all_battles: 
    if not info["playerID"] in battles_info_dict: 
        battles_info_dict[info["playerID"]] = [] 
    battles_info_dict[info["playerID"]].append(info) 

for playerID in [player_info["playerID"] for player_info in all_players_info]: 
    template = {} 
    template["playerID"] = playerID 

    if not playerID in battles_info_dict: 
        continue 

    all_battles_info = battles_info_dict[playerID] 

    if len(all_battles_info) == 0: 
        continue 

    # Compute score for a singler 
    h_sum = 0 
    ab_sum = 0 
    min_year = sys.maxsize 
    max_year = -sys.maxsize - 1 
    for battle_info in all_battles_info: 
        h_sum += int(battle_info["H"]) 
        ab_sum += int(battle_info["AB"]) 

        year = int(battle_info["yearID"]) 
        if year < min_year: 
            min_year = year 

        if year > max_year: 
            max_year = year 

    # Check if under constraint 
    if ab_sum <= 200 or max_year < 1960: 
        continue 

    aver = float(h_sum) / ab_sum 

    all_scores[playerID] = aver 
    
    player_result = {} 
    player_result["playerID"] = playerID 
    player_result["career_hits"] = h_sum 
    player_result["career_at_bats"] = ab_sum 
    player_result["first_year"] = min_year 
    player_result["last_year"] = max_year 

    all_players_result[playerID] = player_result 

# Sort by average score
sorted_scores = sorted(all_scores.items(), key=lambda x: x[1], reverse=True) 

count = 10 
for playerID in sorted_scores: 
    print(all_players_result[playerID[0]]) 
    count -= 1 
    if count < 1: 
        break 
 


