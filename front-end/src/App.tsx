import React, {Component} from 'react';
import './App.css';
import GameSelector from "./GameSelector";
import GameCards from "./GameCards";

interface AppState {
  games: GameObj[];
  suggestions: string[];
  server: string;
}

// Holds the game object: Equivalent to gameobj on the serverside
class GameObj {
    constructor(
        public name: string,
        public genre: string[],
        public developer: string[],
        public publisher: string[],
        public series: string,
        public seriesGames: string[],
        public related: string[],
        public prices: any,
        public platforms: string [],
        public timeToBeat: number,
        public url: string,
        public coverArt: string,
        public opencritic: number,){}
}

class App extends Component<{}, AppState> {
    constructor(props: any) {
        super(props);
        this.state = {
            games: [],
            suggestions: [],
            server: "https://alexl6-playlist.azurewebsites.net/",
        };

        this.loadAllGames = this.loadAllGames.bind(this);
        this.getSuggestion = this.getSuggestion.bind(this);
        this.addGame = this.addGame.bind(this);
        this.clearSearch = this.clearSearch.bind(this);
    }

    /**
     * Trigger the load game method to request all games from the server
     * when the page becomes visible
     */
    componentDidMount() {
        this.loadAllGames();
    }

    /**
     * Load all games in the system upon refresh/initial load
     */
    loadAllGames = async()=>{
        // Make request to Python server
        let url =  this.state.server;
        let responsePromise = fetch(url);
        let response = await responsePromise;
        if (!response.ok) {
            alert("Error " + response.status);
            return;
        }
        let allGames = await response.json();

        // Construct a new game object from the returned data
        let newGameList: GameObj[] = []
        for (let game of allGames) {

            let newGame:GameObj = new GameObj(
                game['name'],
                game['genre'],
                game['developer'],
                game['publisher'],
                game['series'],
                game['series_games'],
                game['related'],
                game['prices'],
                game['platforms'],
                game['time_to_beat'],
                game['url'],
                game['cover_art'],
                game['opencritic']
            );
            newGameList = [...newGameList, newGame]
        }
        this.setState({
            games: newGameList
        })
    }

    /**
     * Get a list of games matching the search term from the server
     * @param keyword Search term from the user
     */
    getSuggestion = async (keyword: string) => {
        console.log(keyword)
        try {
            let url =  this.state.server + "autocomplete?key=" + keyword;
            let responsePromise = fetch(url);
            let response = await responsePromise;
            if (!response.ok) {
                alert("Error " + response.status);
                return;
            }
            let parsedObject = await response.json();
            console.log(parsedObject)
            this.setState({suggestions: parsedObject});
        } catch (e) {
            alert("There was an error getting autocomplete suggestions from the server.\nIs the server running right now?");
            console.log(e);
        }
    }

    /**
     * Add a new game. Passes the name of the game to add to server.
     * Receive the processed game data from the server.
     * @param name Name of the selected game
     */
    addGame = async(name: string) => {
        this.setState({
            suggestions: []
        })
        console.log(name)
        try{
            let url = this.state.server + "addgame?name=" + name;
            let responsePromise = fetch(url);
            let response = await responsePromise;
            if(!response.ok){
                alert("Error " + response.status)
            }
            let parsedObject = await response.json();
            // Construct a new game object from the returned data
            let newGame:GameObj = new GameObj(
                parsedObject['name'],
                parsedObject['genre'],
                parsedObject['developer'],
                parsedObject['publisher'],
                parsedObject['series'],
                parsedObject['series_games'],
                parsedObject['related'],
                parsedObject['prices'],
                parsedObject['platforms'],
                parsedObject['time_to_beat'],
                parsedObject['url'],
                parsedObject['cover_art'],
                parsedObject['opencritic']
            )
            this.setState({
                games: [...this.state.games, newGame]
            })
        } catch (e) {
            alert("There was an error adding game to the server. .\nIs the server running right now?")
        }
    }

    /**
     * Clears the cached search suggestions
     */
    clearSearch(){
        this.setState({suggestions: []})
    }


  render() {
        let gameLibrary = (
            <div className={"library-placeholder"}> Your play list is empty. Add your first game here ⬆️</div>
        );
        if (this.state.games.length !== 0){
            gameLibrary = (<GameCards games={this.state.games}/>);
        }
    return (
        <div className="App">
            <header>Play List 🕹️</header>
                    <GameSelector onClearSearch={this.clearSearch} suggestions={this.state.suggestions} onUpdateSearchTerm={this.getSuggestion} onUpdateGame={this.addGame}/>
                <br/>
            <br/>
            {gameLibrary}
        </div>
        );
    }
}

export default App;
