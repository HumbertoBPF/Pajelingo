import { getGames, getScores } from "./apiUtils.js";
import { connectionErrorElements, loadingElements, noUserScoreElements } from "./feedbackElements.js";

const selected_language_filter = document.querySelector("main .dropdown .dropdown-toggle");
const language_filter_items = document.querySelectorAll("main .dropdown-menu .dropdown-item");
let userScores = document.querySelector("[data-scores]");
const authenticatedUser = document.querySelector("header .account-options .btn-account-options span");
const authenticatedUserName = authenticatedUser?authenticatedUser.innerHTML:null;

if (selected_language_filter != null){
    setUserScoresHTML();    
}

language_filter_items.forEach(item => {
    item.addEventListener("click", (event) => {
        const language = event.target.innerHTML;
        selected_language_filter.innerHTML = language;
        setUserScoresHTML(language);
    });
});

async function setUserScoresHTML() {
    userScores.innerHTML = loadingElements[0];
    userScores.classList = loadingElements[1];

    let language = selected_language_filter.innerHTML.trim();
    const [scoresHTML, userScoresClassList] = await getUserScoresHTML(language);

    setTimeout(function(){
        userScores.innerHTML = scoresHTML;
        userScores.classList = userScoresClassList;
    }, 3000);
}

async function getUserScoresHTML(language) {
    let scores = await getScores(language, authenticatedUserName);

    if (scores != null){
        if (scores.length > 0){
            scores = await getScoreByGameName(scores);
            const scoresHTML = getScoreHTML(scores);
            return [scoresHTML, []];
        }

        return noUserScoreElements;
    }
    
    return connectionErrorElements;
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
