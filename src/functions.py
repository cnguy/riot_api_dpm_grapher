import requests
import src.config as config
from time import sleep

KEY = config.key

REGION_ENDPOINT = "https://" + config.REGION + ".api.pvp.net/api/lol/"
TOO_MANY_REQUESTS = 429

# These functions grab responses.
def get_summoner_id(summoner_name):
    return requests.get(
        REGION_ENDPOINT + config.REGION + "/v1.4/summoner/by-name/" + summoner_name + "?api_key=" + KEY
    ).json()[summoner_name]['id']


def get_match_list(summoner_id):
    """Return a match list by summoner id."""
    return requests.get(
        REGION_ENDPOINT + config.REGION + "/v2.2/matchlist/by-summoner/" + str(summoner_id) + "?api_key=" + KEY
    ).json()


def get_match(matchId):
    match_response = rate_limiter(requests.get(REGION_ENDPOINT + config.REGION + "/v2.2/match/" + str(matchId) + "?api_key=" + str(KEY)))
    print(" => SUCCESS")
    return match_response.json()


def get_champion_name(champion_id):
    """Return a champion name corresponding to the champion id."""
    return requests.get(
        "https://global.api.pvp.net/api/lol/static-data/na/v1.2/champion/" + str(champion_id) + "?api_key=" + KEY
    ).json()['key']


# These functions below use a match response to return specific information.
def get_total_damage_dealt_by_id(match_response, participant_id):
    """Return the total damage dealt by participant id within a match."""
    return match_response['participants'][participant_id-1]['stats']['totalDamageDealtToChampions']
    # participantId is +1 in participantIdentities (within the standard riot json file) ... must account for that


def get_champ_id(match_response, participantId):
    """Return the champion id by participant id within a match."""
    return match_response['participants'][participantId-1]['championId']


def get_match_duration(match_response):
    """Return the match duration in minutes."""
    return match_response['matchDuration']


def get_participant_id(match_response, summoner_id):
    """Return the participantId of the participant within a match."""
    for n in range(0, 10):
        # Find the participant ID of the summoner in the current match.
        if rate_limiter(match_response['participantIdentities'][n]['player']['summonerId']) == summoner_id:
            sleep(1.5)
            return rate_limiter(match_response['participantIdentities'][n]['participantId'])
        sleep(1.5)


def get_matches_with_role(list_response, role, num_of_games):
    """
    Return a list containing matches that all contain the same "role" value.
    {
   "matches": [
      {
         "timestamp": 1464940489115,
         "champion": 236,
         "region": "NA",
         "queue": "TEAM_BUILDER_DRAFT_RANKED_5x5",
         "season": "SEASON2016",
         "matchId": 2205686359,
         "role": "DUO_CARRY",  <--------
         "platformId": "NA1",
         "lane": "BOTTOM"
      },
    ...
    """
    match_ids = []
    count = 0
    i = 0
    while count != num_of_games:
        role_in_match = rate_limiter(list_response['matches'][i]['role'])

        if role_in_match == role:
            sleep(2)
            match_with_role = rate_limiter(list_response['matches'][i]['matchId'])
            match_ids.append(match_with_role)
            sleep(2)
            count += 1
        i += 1

    return match_ids


# Extra functions
def rate_limiter(get):
    response = get
    while str(response) == str(TOO_MANY_REQUESTS):
        print("\n\tExceeded rate limit.")
        print("\tTrying again in 5 seconds...")
        sleep(5)
        response = get
    return response


def convert_to_minutes_seconds(seconds):
    a = seconds / 60
    a,b = divmod(a, 1.0)
    b *= 60
    c = str(round(b))

    # just for formatting
    if len(str(c)) == 1:
        c = "0" + c
    return str(int(a)) + ":" + c


def calculate_dpm(total_damage, minutes):
    return round(total_damage / minutes)