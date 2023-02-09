const baseUrl = window.location.origin;
export const loadingElement = `<div class="text-center col-6">
                                    <img id="noResultImg" src="/static/images/loading.gif" class="img-fluid rounded col-8 col-sm-4 col-md-3 col-lg-2" alt="No results image">
                                    <p id="noResultP">Please, wait...</p>
                                </div>`;

export async function getRankings(language, page=null) {
    let url = `${baseUrl}/api/rankings/?language=${language}`;

    if (page){
        url += `&page=${page}`;
    }

    const response = await fetch(url);
    return response.ok?(await response.json()):null;
}

export async function getScores(language, user=null) {
    let url = `${baseUrl}/api/scores/?language=${language}`;

    if (user){
        url += `&user=${user}`;
    }
    
    const response = await fetch(url);
    return response.ok?(await response.json()):null;
}

export async function getGames() {
    let url = `${baseUrl}/api/games`;
    
    const response = await fetch(url);
    return response.ok?(await response.json()):null;
}