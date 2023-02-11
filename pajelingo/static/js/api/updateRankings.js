import { getRankings } from "./apiUtils.js";
import { connectionErrorElements, emptyRankingsElements, loadingElements } from "./feedbackElements.js";

const selected_language_filter = document.querySelector("main .dropdown .dropdown-toggle");
const language_filter_items = document.querySelectorAll("main .dropdown-menu .dropdown-item");
let rankingContent = document.querySelector("[data-ranking]");
const authenticatedUser = document.querySelector("header .account-options .btn-account-options span");
const authenticatedUserName = authenticatedUser?authenticatedUser.innerHTML:null;
let currentPage = 1;

if (selected_language_filter != null){
    setRankingHTML();
}

language_filter_items.forEach(item => {
    item.addEventListener("click", (event) => {
        currentPage = 1;
        const language = event.target.innerHTML;
        selected_language_filter.innerHTML = language;
        setRankingHTML();
    });
});

async function setRankingHTML() {
    rankingContent.innerHTML = loadingElements[0];
    rankingContent.classList = loadingElements[1];
    getPagination(null);

    let language = selected_language_filter.innerHTML.trim();
    const [rankingHTML, rankingClassList] = await getRankingHTML(language); 

    setTimeout(() => {
        rankingContent.innerHTML = rankingHTML;
        rankingContent.classList = rankingClassList;
        setPaginationButtons();
    }, 3000);
}

async function getRankingHTML(language) {
    const ranking = await getRankings(language, null, currentPage);

    if (ranking != null){
        const rankingScores = ranking.results;

        if ((rankingScores != null) && (rankingScores.length > 0)){
            let myPositionHTML = "";
            
            if (authenticatedUserName != null) {
                const userRanking = await getRankings(language, authenticatedUserName);

                if (userRanking != null) {
                    const userRankingScore = userRanking.results;

                    if ((userRankingScore != null) && (userRankingScore.length === 1)){
                        myPositionHTML = parseMyPositionHTML(userRankingScore[0]);
                    }
                }else{
                    return connectionErrorElements;
                }
            }

            const generalRankingHTML = parseGeneralRankingHTML(rankingScores);
            const paginationHTML = getPagination(ranking);
            const rankingHTML = `<table class="table table-striped">
                                    <thead>
                                        <tr>
                                            <th scope="col">Position</th>
                                            <th scope="col">Username</th>
                                            <th scope="col">Score</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${generalRankingHTML + myPositionHTML}
                                    </tbody>
                                </table>
                                ${paginationHTML}`;
            return [rankingHTML, []];
        }

        return emptyRankingsElements;
    }
    
    return connectionErrorElements;
}

function parseGeneralRankingHTML(rankingData) {
    let rankingDataHTML = "";

    rankingData.forEach((item, index) => {
        rankingDataHTML += `<tr>
            <td>${10*(currentPage-1) + index + 1}</td>
            <td>${item.user}</td>
            <td>${item.score}</td>
        </tr>`;
    });

    return rankingDataHTML;
}

function parseMyPositionHTML(userScore) {
    return `<tr>
        <td>...</td>
        <td>...</td>
        <td>...</td>
    </tr>
    <tr>
        <th scope="row">(You) ${userScore.position}</th>
        <th scope="row">${userScore.user}</th>
        <th scope="row">${userScore.score}</th>
    </tr>`;
}

function getPagination(ranking) {
    if (ranking != null){
        const hasPrevious = (ranking.previous != null)
        const hasNext = (ranking.next != null);

        if (hasPrevious || hasNext){        
            let previousButton = hasPrevious?`<li class="page-item">
                                                <a class="page-link" aria-label="Previous" data-previous-button>&laquo;</a>
                                            </li>`:"";
            let nextButton = hasNext?`<li class="page-item">
                                        <a class="page-link" aria-label="Next" data-next-button>&raquo;</a>
                                    </li>`:"";

            let pageButtons = getPageButtons(ranking);

            return `<nav aria-label="Page navigation example">
                        <ul class="pagination">
                            ${previousButton}
                            ${pageButtons}
                            ${nextButton}
                        </ul>
                    </nav>`;
        }
    }

    return "";
}

function getPageButtons(ranking){
    const numberPages = Math.ceil(ranking.count/10);
    let pageButtons = "";

    for (let i=1;i<=numberPages;i++) {
        if (i === currentPage) {
            pageButtons += `<li class="page-item active"><a class="page-link" data-page-button>${currentPage}</a></li>`;
        }else if (i === 1) {
            pageButtons += `<li class="page-item"><a class="page-link" data-page-button>1</a></li>`;
        }else if (i === numberPages) {
            pageButtons += `<li class="page-item"><a class="page-link" data-page-button>${numberPages}</a></li>`;
        }else if ((i == 2) || (i == numberPages-1)) {
            pageButtons += `<li class="page-item"><a class="page-link">...</a></li>`;
        }
    }

    return pageButtons;
}

function setPaginationButtons() {
    setPaginationButton(".pagination .page-item [data-previous-button]", currentPage-1);
    setPaginationButton(".pagination .page-item [data-next-button]", currentPage+1);
    setPaginationButton(".pagination .page-item [data-page-button]");
}

function setPaginationButton(selector, page=null) {
    let pageButtons = document.querySelectorAll(selector);
    pageButtons.forEach((pageButton) => {
        pageButton.addEventListener("click", () => {
            currentPage = (page==null)?(parseInt(pageButton.innerHTML, 10)):page;
            setRankingHTML(currentPage);
        });
    });
}