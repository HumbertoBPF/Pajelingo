const baseUrl = window.location.origin;

export async function getRankings(language, user=null, page=null) {
    let url = `${baseUrl}/api/rankings/?language=${language}`;

    if (user) {
        url += `&user=${user}`
    }

    if (page) {
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