# Import packages
import urllib.request, urllib.parse, urllib.error
import json
from flask import Flask, request, abort
from hltbapi import HtmlScraper
from gameobj import GameObj

# Import helper class
from typing import List, Dict

from IGDBHandler import IGDBHandler
from ITADHandler import ITADHandler
import OCHandler
from keys import IGDB_ID, IGDB_secret, ITAD_key

# Initialize external handlers
IGDB: IGDBHandler = IGDBHandler(IGDB_ID, IGDB_secret)
ITAD: ITADHandler = ITADHandler(ITAD_key)

# Create new flask app
app = Flask(__name__)

# Global variables
games: List[GameObj] = []
genres_dict: Dict[str, int] = {}


# Helper functions
def add_game(keyword: str) -> None:
    # Lookup in IGDB
    IGDB_res = IGDB.search_game(keyword)
    # Stops if the game doesn't exist as an entry in IGDB
    if len(IGDB_res) == 0:
        return
    IGDB_res = IGDB_res[0]
    # Extract useful data form the response
    full_name = IGDB_res['name']
    # Get game genres
    genres = []
    if 'genres' in IGDB_res: # maybe add the following code     and len(IGDB_res['genres']) > 0:
        genres = [x['name'] for x in IGDB_res['genres']]

    # Add genre to the overall genre dictionary
    for g in genres:
        genres_dict[g] = genres_dict.get(g, 0) + 1

    # Get game developer
    devs: List[str] = []
    publishers: List[str] = []
    if 'involved_companies' in IGDB_res:
        temp = [x['company']['name'] for x in IGDB_res['involved_companies'] if x['developer'] == True]
        if len(temp) > 0:
            devs = temp[:min(2,len(temp))]

        temp = [x['company']['name'] for x in IGDB_res['involved_companies'] if x['publisher'] == True]
        if len(temp) > 0:
            publishers = temp[:min(2, len(temp))]

    # Get available platforms
    platforms: List[Dict[str, str]] = []
    if 'platforms' in IGDB_res and len(IGDB_res['platforms']) > 0:
        # TODO: Fix this
        platforms = [{'name': x['name'], 'logo': x['platform_logo']['url']} for x in IGDB_res['platforms']]

    # Game series
    series: Dict = {'name': 'N/A', 'games': []}
    if 'collection' in IGDB_res and len(IGDB_res['collection']['games']) > 0:
        series['name'] = IGDB_res['collection']['name']
        series['games'] = [x['name'] for x in IGDB_res['collection']['games'] if x['category'] in {0, 6, 8, 9, 10, 11}]

    # Realted games
    related: List[str] = []
    if 'similar_games' in IGDB_res and len(IGDB_res['similar_games']) > 0:
        related = [x['name'] for x in IGDB_res['similar_games']]


    # Lookup in ITAD
    # TODO: Implement full ITAD feature set
    plain = ITAD.search(full_name)
    prices = {'price': -1, 'lowest': -1, 'stores': List[str]}
    if plain is not None:
        lowest = ITAD.load_historical_low([plain])
        prices['lowest'] = lowest[plain][0]['price']
    else:
        prices['stores'] = []

    # Load OC score
    search_res = OCHandler.search(full_name)
    if OCHandler.check_validity(search_res):
        ID = OCHandler.top_id(search_res)
        OC_score = int(OCHandler.top_critic_score(OCHandler.get_review(ID)))
    else:
        OC_score = -1

    # Time to beat the game
    try:
        TTB = HtmlScraper().search(name=full_name)
        TTB = TTB[0].gameplayMain
    except Exception:
        # Using a generic Exception here because the unofficial HowLongToBeat API doesn't seem to handle errors
        print("Unable to find this game on HowLongToBeat.com")
        TTB = -1

    # TODO: Fix price
    new_game = GameObj(full_name, genres, devs, publishers, series, related, prices, platforms,
                       TTB, "url", "art", OC_score)

    # Add the newly created game object to the list
    games.append(new_game)



# Flask handlers
@app.route("/")
def main_handler():
    name = request.args.get('username')
    if name is None:
        abort(400)
    dummy = {"key": "value"}
    return json.dumps(dummy)

# res = HtmlScraper().search(name=input("Enter a game:\n"))
# for entry in res:
#     print('===================================')
#     print(entry.detailId)
#     print(entry.gameName)
#     print(entry.imageUrl)
#     print(entry.timeLabels)
#     print(entry.gameplayMain)
#     print(entry.gameplayMainExtra)
#     print(entry.gameplayCompletionist)
#     print('===================================')


# rawHTML = urllib.request.urlopen('https://store.steampowered.com/search/?filter=topsellers')
# doc = rawHTML.read().decode('utf8')
# soup:BeautifulSoup = BeautifulSoup(doc, 'html.parser')
# top_games = soup.findAll("span", class_="title")
# print(top_games)

# Main method
if __name__ == "__main__":
    # Initialize external helper objects to handle requests/API calls
    IGDB: IGDBHandler = IGDBHandler(IGDB_ID, IGDB_secret)
    ITAD: ITADHandler = ITADHandler(ITAD_key)

    keyword = input("Enter the name of a game:\n")
    # Lookup in IGDB
    data1 = IGDB.search_game(keyword)[0]
    full_name = data1['name']

    # Lookup in ITAD
    plain = ITAD.search(full_name)
    lowest = ITAD.load_historical_low([plain])
    lowest_price = lowest[plain][0]['price']

    # Load OC score
    ID = OCHandler.top_id(OCHandler.search(full_name))
    OC_Score = OCHandler.top_critic_score(OCHandler.get_review(ID))

    # Time to beat the game
    TTB = HtmlScraper().search(name=full_name)[0].gameplayMain

    print()
    print("=====%s=====" % data1['name'])
    print("Genre: %s" % ", ".join(x['name'] for x in data1['genres']))
    print("Developed by: %s" % [x['company']['name'] for x in data1['involved_companies'] if x['developer'] == True][0])
    print("Published by: %s" % [x['company']['name'] for x in data1['involved_companies'] if x['publisher'] == True][0])
    print("Historic low price on Steam: %s" % str(round(lowest_price, 2)))
    print("Average time to beat: %d hrs" % int(TTB))
    print("OpenCritic score: %d" % OC_Score)

    # Host of localhost when testing
    app.run(host="localhost", port=8080, debug=True)