import { getScores, loadingElement } from "./apiUtils.js";

const selected_language_filter = document.querySelector("main .dropdown .dropdown-toggle");
const language_filter_items = document.querySelectorAll("main .dropdown-menu .dropdown-item");
let rankingContent = document.querySelector("[data-ranking]");
const authenticatedUser = document.querySelector("header .account-options .btn-account-options span");
const authenticatedUserName = authenticatedUser?authenticatedUser.innerHTML:null;

if (selected_language_filter != null){
    let defaultLanguage = selected_language_filter.innerHTML.trim();
    setRankingData(defaultLanguage);
}

language_filter_items.forEach(item => {
    item.addEventListener("click", (event) => {
        const language = event.target.innerHTML;
        selected_language_filter.innerHTML = language;
        setRankingData(language);
    });
});

async function setRankingData(language) {
    rankingContent.innerHTML = loadingElement;
    rankingContent.classList = ["row justify-content-center"];

    let scores = await getScores(language);

    let rankingHTML = "";
    let rankingClassList = [];

    if (scores != null){
        if (scores.length == 0){
           rankingHTML = "<p>It seems that no one has played this game yet... Be the first to play it and get ahead the other competitors!</p>";
        } else{
            scores = groupScoresByUser(scores);
            const rankingData = sortRankingData(scores);
            rankingHTML = getRankingHTML(rankingData);
        }
    }else{
        rankingHTML = `<div class="text-center col-sm-8 col-md-4">
                            <img id="noResultImg" src="/static/images/error.jpg" class="img-fluid rounded" alt="No results image">
                            <p id="noResultP">Connection error</p>
                        </div>`;
        rankingClassList = ["row justify-content-center"];
    }

    setTimeout(function(){
        rankingContent.innerHTML = rankingHTML;
        rankingContent.classList = rankingClassList;
    }, 3000);
}

function groupScoresByUser(scores) {
    let userScores = new Map();

    scores.forEach(item => {
        const currentValue = userScores.get(item.user);

        if (!currentValue) {
            userScores.set(item.user, item.score);
        }else {
            userScores.set(item.user, currentValue + item.score);
        }
    });

    let rankingData = []

    for (const [key, value] of userScores.entries()) {
        rankingData = [...rankingData, {
            user: key,
            score: value
        }]
    }

    return rankingData;
}

function sortRankingData(scores) {
    scores.sort(function(a, b) {
        return (b.score - a.score)
    });

    return scores;
}

function getRankingHTML(rankingData) {
    let rankingDataHTML = "";
    let myPositionHTML = "";

    rankingData.forEach((item, index) => {
        rankingDataHTML += `<tr>
            <td>${index + 1}</td>
            <td>${item.user}</td>
            <td>${item.score}</td>
        </tr>`;

        if (authenticatedUserName != null) {
            if (authenticatedUserName === item.user){
                myPositionHTML = `<tr>
                    <td>...</td>
                    <td>...</td>
                    <td>...</td>
                </tr>
                <tr>
                    <th scope="row">(You) ${index + 1}</th>
                    <th scope="row">${item.user}</th>
                    <th scope="row">${item.score}</th>
                </tr>`;
            }
        }
    });

    return `<table class="table table-striped">
                <thead>
                    <tr>
                        <th scope="col">Position</th>
                        <th scope="col">Username</th>
                        <th scope="col">Score</th>
                    </tr>
                </thead>
                <tbody>
                    ${rankingDataHTML + myPositionHTML}
                </tbody>
            </table>`;
}