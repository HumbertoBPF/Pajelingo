import { getGames, getScores, loadingElement } from "./apiUtils.js";

const selected_language_filter = document.querySelector("main .dropdown .dropdown-toggle");
const language_filter_items = document.querySelectorAll("main .dropdown-menu .dropdown-item");
let userScores = document.querySelector("[data-scores]");
const authenticatedUser = document.querySelector("header .account-options .btn-account-options span");
const authenticatedUserName = authenticatedUser?authenticatedUser.innerHTML:null;

if (selected_language_filter != null){
    let defaultLanguage = selected_language_filter.innerHTML.trim();
    setScoreData(defaultLanguage);    
}

language_filter_items.forEach(item => {
    item.addEventListener("click", (event) => {
        const language = event.target.innerHTML;
        selected_language_filter.innerHTML = language;
        setScoreData(language);
    });
});

async function setScoreData(language) {
    userScores.innerHTML = loadingElement;
    userScores.classList = ["row justify-content-center"];

    let scores = await getScores(language, authenticatedUserName);

    let scoresHTML = "";
    let userScoresClassList = [];

    if (scores != null){
        if (scores.length == 0){
            scoresHTML = "<p id='warningNoScores'>It seems that you haven't played games in this language yet...</p>";
        } else{
            scores = await getScoreByGameName(scores);
            scoresHTML = getScoreHTML(scores);
        }
    }else{
        scoresHTML = `<div class="text-center col-sm-8 col-md-4">
                            <img id="noResultImg" src="/static/images/error.jpg" class="img-fluid rounded" alt="No results image">
                            <p id="noResultP">Connection error</p>
                        </div>`;

        userScores.classList = ["row justify-content-center"];
    }

    setTimeout(function(){
        userScores.innerHTML = scoresHTML;
        userScores.classList = userScoresClassList;
    }, 3000);
}

async function getScoreByGameName(scores) {
    let games = await getGames();
    // Replacing game id with the corresponding game name
    let gameById = new Map();

    games.forEach(game => {
        gameById.set(game.id, game.game_name);
    });

    scores = scores.map(score => {
        score.game = gameById.get(score.game);
        return score;
    });
    // Sorting scores by game in the ascending order
    scores.sort(function(a, b) {
        let gameA = a.game.toUpperCase();
        let gameB = b.game.toUpperCase();
        if (gameA < gameB) {
            return -1;
        }
        if (gameA > gameB) {
            return 1;
        }
        return 0;
    });

    return scores;
}

function getScoreHTML(scores) {
    let tableBody = "";

    scores.forEach(score => {
        tableBody += `<tr>
            <td>${score.game}</td>
            <td>${score.score}</td>
        </tr>`;
    });

    return `<table class="table table-striped">
                <thead>
                    <tr>
                        <th scope="col">Game</th>
                        <th scope="col">Score</th>
                    </tr>
                </thead>
                <tbody>
                    ${tableBody}
                </tbody>
            </table>`; 
}
