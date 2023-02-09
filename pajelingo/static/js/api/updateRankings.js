import { getRankings, loadingElement } from "./apiUtils.js";

const selected_language_filter = document.querySelector("main .dropdown .dropdown-toggle");
const language_filter_items = document.querySelectorAll("main .dropdown-menu .dropdown-item");
let rankingContent = document.querySelector("[data-ranking]");
let pagination = document.querySelector("[data-pagination]");
const authenticatedUser = document.querySelector("header .account-options .btn-account-options span");
const authenticatedUserName = authenticatedUser?authenticatedUser.innerHTML:null;
let currentPage = 1;

if (selected_language_filter != null){
    setRankingData();
}

language_filter_items.forEach(item => {
    item.addEventListener("click", (event) => {
        currentPage = 1;
        const language = event.target.innerHTML;
        selected_language_filter.innerHTML = language;
        setRankingData();
    });
});

async function setRankingData(page=null) {
    rankingContent.innerHTML = loadingElement;
    rankingContent.classList = ["row justify-content-center"];
    addPagination(null);

    let language = selected_language_filter.innerHTML.trim();
    let ranking = await getRankings(language, page);

    let rankingHTML = "";
    let rankingClassList = [];

    if (ranking != null){
        if (ranking.length == 0){
           rankingHTML = "<p>It seems that no one has played this game yet... Be the first to play it and get ahead the other competitors!</p>";
        } else{
            rankingHTML = getRankingHTML(ranking.results);
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
        addPagination(ranking);
    }, 3000);
}

function getRankingHTML(rankingData) {
    let rankingDataHTML = "";
    let myPositionHTML = "";

    rankingData.forEach((item, index) => {
        rankingDataHTML += `<tr>
            <td>${10*(currentPage-1) + index + 1}</td>
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


function addPagination(ranking) {
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

            pagination.innerHTML = `<nav aria-label="Page navigation example">
                                        <ul class="pagination">
                                            ${previousButton}
                                            ${pageButtons}
                                            ${nextButton}
                                        </ul>
                                    </nav>`;

            setPaginationButton(".pagination .page-item [data-previous-button]", currentPage-1)
            setPaginationButton(".pagination .page-item [data-next-button]", currentPage+1)
            setPaginationButton(".pagination .page-item [data-page-button]")

            return;
        }
    }

    pagination.innerHTML = "";
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

function setPaginationButton(selector, page=null) {
    let pageButtons = document.querySelectorAll(selector);
    pageButtons.forEach((pageButton) => {
        pageButton.addEventListener("click", ()=>{
            currentPage = (page==null)?(parseInt(pageButton.innerHTML, 10)):page;
            setRankingData(currentPage);
        });
    });
}