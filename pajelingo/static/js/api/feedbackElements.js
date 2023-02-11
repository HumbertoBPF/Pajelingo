const errorMessage = `<div class="text-center col-sm-8 col-md-4">
                        <img id="noResultImg" src="/static/images/error.jpg" class="img-fluid rounded" alt="No results image">
                        <p id="noResultP">Connection error</p>
                    </div>`;
const errorClassList = ["row justify-content-center"];

const noUserScoreMessage = "<p id='warningNoScores'>It seems that you haven't played games in this language yet...</p>";

const emptyRankingsMessage = "<p>It seems that no one has played this game yet... Be the first to play it and get ahead the other competitors!</p>";

const loadingMessage = `<div class="text-center col-6">
                            <img id="noResultImg" src="/static/images/loading.gif" class="img-fluid rounded col-8 col-sm-4 col-md-3 col-lg-2" alt="No results image">
                            <p id="noResultP">Please, wait...</p>
                        </div>`;

export const connectionErrorElements = [errorMessage, errorClassList];
export const noUserScoreElements = [noUserScoreMessage, []];
export const emptyRankingsElements = [emptyRankingsMessage, []];
export const loadingElements = [loadingMessage, errorClassList];