#This script tracks the elimination dates of NBA playoff teams

import pandas as pd

numDivision = 16 #Games played in division
numConference = 52 #Games played in conference

#Defines a team and keeps track of record
class Team:
    def __init__(self, name,losses, gamesLeft, isEliminated, eliminationDate, divisionWins, divisionLosses, conferenceWins, conferenceLosses):
        self.name = name
        #self.conference = conference
        self.losses = losses
        self.gamesLeft = gamesLeft
        self.isEliminated = isEliminated
        self.eliminationDate = eliminationDate
        self.divisionWins = divisionWins
        self.divisionLosses = divisionLosses
        self.conferenceWins = conferenceWins
        self.conferenceLosses = conferenceLosses

    def win(self, isConference, isDivision):
        self.gamesLeft = self.gamesLeft - 1
        if isConference:
            self.conferenceWins = self.conferenceWins + 1
            if isDivision:
                self.divisionWins = self.divisionWins + 1

    def loss(self, isConference, isDivision):
        self.losses = self.losses + 1
        self.gamesLeft = self.gamesLeft - 1
        if isConference:
            self.conferenceLosses = self.conferenceLosses + 1
            if isDivision:
                self.divisionLosses = self.divisionLosses + 1

    def eliminated(self, date):
        self.isEliminated = True
        self.eliminationDate = date

    def printRecord(self):
        print self.name + ", w: " + str(82 - self.gamesLeft - self.losses) + ", l: " + str(self.losses)

conferences = pd.read_csv('Conferences.csv')
eastTeams = conferences[conferences['Conference_id'] == 'East']['Team_Name'].tolist()
westTeams = conferences[conferences['Conference_id'] == 'West']['Team_Name'].tolist()
conferences.set_index('Team_Name', inplace=True)

gamesAgainst = dict() #Tracks all head to head matchups

eastTracker = dict()
westTracker = dict()

for team in eastTeams:
    eastTracker[team] = Team(team, 0, 82, False, "Playoffs", 0, 0, 0, 0)

for team in westTeams:
    westTracker[team] = Team(team, 0, 82, False, "Playoffs", 0, 0, 0, 0)

conferenceH2H = dict() #Stores teams in alphabetical order and games won by team1

#Go through the first half of season without checking (impossible to get eliminated in 40 games
#Go through 2016
firstHalf = open('FirstHalf.csv')
next(firstHalf) #skips header line
for line in firstHalf:
    sameConference = False
    sameDivision = False
    #Find conferences and divisions
    result = line.split(',')
    #Assume home team is winner
    if result[1] < result[2]:
        gamesAgainst[result[1] + '-' + result[2]] = gamesAgainst.get(result[1] + '-' + result[2], 0) + 1
    if result[2] < result[1]:
        gamesAgainst[result[2] + '-' + result[1]] = gamesAgainst.get(result[2] + '-' + result[1], 0) + 1
    winner = result[1]
    loser = result[2]
    if result[5].rstrip() == 'Away':
        winner = result[2]
        loser = result[1]
    winnerConference = conferences.loc[winner]['Conference_id']
    loserConference = conferences.loc[loser]['Conference_id']
    if winnerConference == loserConference:
        sameConference = True
        if conferences.loc[result[1]]['Division_id'] == conferences.loc[result[2]]['Division_id']:
            sameDivision = True
        if winner < loser:
            conferenceH2H[winner + '-' + loser] = conferenceH2H.get(winner + '-' + loser, 0) + 1

        if loser < winner:
            conferenceH2H[loser + '-' + winner] = conferenceH2H.get(loser + '-' + winner, 0) + 0
    if(winnerConference == 'East'):
        eastTracker[winner].win(sameConference, sameDivision)
    else:
        westTracker[winner].win(sameConference, sameDivision)
    if(loserConference == 'East'):
        eastTracker[loser].loss(sameConference, sameDivision)
    else:
        westTracker[loser].loss(sameConference, sameDivision)


secondHalf = open('SecondHalf.csv')
htohleft = dict()

for line in secondHalf:
    result = line.split(',')
    if result[1] < result[2]:
        gamesAgainst[result[1] + '-' + result[2]] = gamesAgainst.get(result[1] + '-' + result[2], 0) + 1
    if result[2] < result[1]:
        gamesAgainst[result[2] + '-' + result[1]] = gamesAgainst.get(result[2] + '-' + result[1], 0) + 1
    homeConference = conferences.loc[result[1]]['Conference_id']
    awayConference = conferences.loc[result[2]]['Conference_id']
    if homeConference != awayConference:
        continue
    else:
        if result[1] < result[2]:
            htohleft[result[1] + '-' + result[2]] = htohleft.get(result[1] + '-' + result[2], 0) + 1
        else:
            htohleft[result[2] + '-' + result[1]] = htohleft.get(result[2] + '-' + result[1], 0) + 1


secondHalf.close()
secondHalf = open('SecondHalf.csv')

date = "1/1/2017"
previousDate = "1/1/2017"
for line in secondHalf:
    checkElimination = False
    sameConference = False
    sameDivision = False
    #Find conferences and divisions
    result = line.split(',')
    date = result[0]
    if previousDate != date:
        sortedWest = sorted(westTracker.values(), key=lambda x: x.losses)
        sortedEast = sorted(eastTracker.values(), key=lambda x: x.losses)

        maxLossesWest = sortedWest[7].losses + sortedWest[7].gamesLeft
        maxLossesEast = sortedEast[7].losses + sortedEast[7].gamesLeft
        # Checking dependencies
        eightSeeds = list()
        eightSeeds.append(sortedWest[7])
        for i in range(7, 13):
            for j in range(i + 1, 14):
                if maxLossesWest - sortedWest[j].losses - sortedWest[j].gamesLeft >= 4:
                    continue
                if sortedWest[i].name < sortedEast[j].name:  # check if games are left
                    continue
        for team in sortedWest[8:]:
            if team.isEliminated == True:
                continue
            if maxLossesWest < team.losses:
                team.eliminated(previousDate)
            if maxLossesWest == team.losses:  # Go through tiebreak rules
                for eightSeed in eightSeeds:
                    # check head to head
                    matchup = ""
                    lotteryWins = 0
                    if team.name < eightSeed.name:
                        matchup = team.name + '-' + eightSeed.name
                        print matchup
                        teamWins = conferenceH2H[matchup]
                        totalGames = gamesAgainst[matchup]
                        left = htohleft[matchup]
                        if teamWins + left < totalGames - teamWins - left:
                            team.eliminated(result[0])
                            break
                        if left == 0 and teamWins == totalGames - teamWins:
                            # check if team will win division
                            # check division W-L
                            continue
                    else:
                        matchup = eightSeed.name + '-' + team.name
                        teamWins = conferenceH2H[matchup]
                        totalGames = gamesAgainst[matchup]
                        left = htohleft.get(matchup, 0)
                        if teamWins > totalGames - teamWins:
                            team.eliminated(result[0])
                            break
                        if left == 0 and teamWins == totalGames - teamWins:
                            # check if team will win division
                            # check division W-L
                            continue

        eightSeedsEast = list()
        eightSeedsEast.append(sortedEast[7])

        for team in sortedEast[8:]:
            if team.isEliminated == True:
                continue
            if maxLossesEast < team.losses:
                team.eliminated(result[0])
            if maxLossesEast == team.losses:  # Go through tiebreak rules
                for eightSeed in eightSeedsEast:
                    # check head to head
                    matchup = ""
                    lotteryWins = 0
                    if team.name < eightSeed.name:
                        matchup = team.name + '-' + eightSeed.name
                        teamWins = conferenceH2H[matchup]
                        totalGames = gamesAgainst[matchup]
                        left = htohleft[matchup]
                        if teamWins + left < totalGames - teamWins - left:
                            team.eliminated(result[0])
                            break
                        if left == 0 and teamWins == totalGames - teamWins:
                            # check if team will win division
                            # check division
                            continue
                    else:
                        matchup = eightSeed.name + '-' + team.name
                        teamWins = conferenceH2H[matchup]
                        totalGames = gamesAgainst[matchup]
                        left = htohleft[matchup]
                        if teamWins > totalGames - teamWins:
                            team.eliminated(result[0])
                            break
                        if left == 0 and teamWins == totalGames - teamWins:
                            # check if team will win division
                            # check division W-L
                            continue

    #Assume home team is winner
    winner = result[1]
    loser = result[2]
    if result[5].rstrip() == 'Away':
        winner = result[2]
        loser = result[1]
    winnerConference = conferences.loc[winner]['Conference_id']
    loserConference = conferences.loc[loser]['Conference_id']
    if winnerConference == loserConference:
        sameConference = True
        if (winner < loser):
            conferenceH2H[winner + '-' + loser] = conferenceH2H.get(winner + '-' + loser, 0) + 1
            htohleft[winner + '-' + loser] = htohleft.get(winner + '-' + loser, 0) - 1
        if (loser < winner):
            conferenceH2H[loser + '-' + winner] = conferenceH2H.get(loser + '-' + winner, 0) + 0
            htohleft[loser + '-' + winner] = htohleft.get(loser + '-' + winner, 0) - 1

        if conferences.loc[result[1]]['Division_id'] == conferences.loc[result[2]]['Division_id']:
            sameDivision = True
    if(winnerConference == 'East'):
        eastTracker[winner].win(sameConference, sameDivision)
    else:
        westTracker[winner].win(sameConference, sameDivision)
    if(loserConference == 'East'):
        eastTracker[loser].loss(sameConference, sameDivision)
    else:
        westTracker[loser].loss(sameConference, sameDivision)


    previousDate = result[0]

sortedWest = sorted(westTracker.values(), key=lambda x: x.losses)
sortedEast = sorted(eastTracker.values(), key=lambda x: x.losses)
maxLossesWest = sortedWest[7].losses + sortedWest[7].gamesLeft
maxLossesEast = sortedEast[7].losses + sortedEast[7].gamesLeft

eightSeedsEast = list()
eightSeedsEast.append(sortedEast[7])

eightSeeds = list()
eightSeeds.append(sortedWest[7])

for team in sortedEast[8:]:
    if team.isEliminated == True:
        continue
    if maxLossesEast < team.losses:
        team.eliminated(result[0])
    if maxLossesEast == team.losses:  # Go through tiebreak rules
        for eightSeed in eightSeedsEast:
            # check head to head
            matchup = ""
            lotteryWins = 0
            if team.name < eightSeed.name:
                matchup = team.name + '-' + eightSeed.name
                teamWins = conferenceH2H[matchup]
                totalGames = gamesAgainst[matchup]
                left = htohleft[matchup]
                if teamWins + left < totalGames - teamWins - left:
                    team.eliminated(result[0])
                    break
                if left == 0 and teamWins == totalGames - teamWins:
                    # check if team will win division
                    # check division
                    continue
            else:
                matchup = eightSeed.name + '-' + team.name
                teamWins = conferenceH2H[matchup]
                totalGames = gamesAgainst[matchup]
                left = htohleft[matchup]
                if teamWins > totalGames - teamWins:
                    team.eliminated(result[0])
                    break
                if left == 0 and teamWins == totalGames - teamWins:
                    # check if team will win division
                    # check division W-L
                    continue

for team in sortedWest[8:]:
    if team.isEliminated == True:
        continue
        if maxLossesWest < team.losses:
            team.eliminated(previousDate)
        if maxLossesWest == team.losses:  # Go through tiebreak rules
            for eightSeed in eightSeeds:
                # check head to head
                matchup = ""
                lotteryWins = 0
                if team.name < eightSeed.name:
                    matchup = team.name + '-' + eightSeed.name
                    print matchup
                    teamWins = conferenceH2H[matchup]
                    totalGames = gamesAgainst[matchup]
                    left = htohleft[matchup]
                    if teamWins + left < totalGames - teamWins - left:
                        team.eliminated(result[0])
                        break
                    if left == 0 and teamWins == totalGames - teamWins:
                        # check if team will win division
                        # check division W-L
                        continue
                else:
                    matchup = eightSeed.name + '-' + team.name
                    teamWins = conferenceH2H[matchup]
                    totalGames = gamesAgainst[matchup]
                    left = htohleft.get(matchup, 0)
                    if teamWins > totalGames - teamWins:
                        team.eliminated(result[0])
                        break
                    if left == 0 and teamWins == totalGames - teamWins:
                        # check if team will win division
                        #  check division W-L
                        continue

allTeams = dict(eastTracker.items())
allTeams.update(westTracker.items())

with open("finalDates.csv", 'w') as file:
    for team in sorted(allTeams.values(), key=lambda x: x.name):
        file.write(team.name + "," + team.eliminationDate)
        file.write("\n")

# for matchup in conferenceH2H.items():
#     print matchup
#
# print "akjfdskjfskfnkdsnkfdsnkfdsfdskjdsndsfnfdskjds \n\n\n\n"
#
# for games in htohleft.items():
#     print games









