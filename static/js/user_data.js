function getObject(key) {
    return JSON.parse(localStorage.getItem(key));
}

function setObject(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
}

export function getSeenEpisodes(anime = undefined) {
    const animes = getObject('seen');
    if (!animes) {
        return anime ? [] : {};
    }
    return anime ? animes[anime] || [] : animes;
}

export function isSeenEpisode(anime, episode) {
    return getSeenEpisodes(anime).includes(episode);
}

export function seenEpisode(anime, episode) {
    const animes = getSeenEpisodes();
    if (!animes[anime]) {
        animes[anime] = [];
    }
    animes[anime].push(episode);
    setObject('seen', animes);
}

export function unseenEpisode(anime, episode) {
    const animes = getSeenEpisodes();
    if (!animes[anime]) {
        return;
    }

    const index = animes[anime].indexOf(episode);
    if (index !== -1) {
        animes[anime].splice(index, 1);
        setObject('seen', animes);
    }
}

export function seenAnime(anime, episodes) {
    for (const episode of episodes) {
        seenEpisode(anime, episode);
    }
}

export function unseenAnime(anime) {
    const animes = getObject('seen');
    animes[anime] = undefined;
    setObject('seen', animes);
}

export function getFavAnimes() {
    return getObject('favs') || [];
}

export function isFavAnime(anime) {
    return getFavAnimes().includes(anime);
}

export function favAnime(anime) {
    const animes = getFavAnimes();
    setObject('favs', [...new Set(animes.concat([anime]))]);
}

export function unfavAnime(anime) {
    const animes = getFavAnimes();
    const index = animes.indexOf(anime);
    if (index !== -1) {
        animes.splice(index, 1);
        setObject('favs', animes);
    }
}
