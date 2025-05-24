from json import loads, dumps
from os import getenv
from re import search
from sys import argv
from urllib.parse import quote
from urllib.request import urlopen

PATTERN = r'var ytInitialData =(.+)"targetId":"search-page"};</script>'


def yt_search(query, top_k=1):
    url = f"https://www.youtube.com/results?search_query={quote(query)}"

    with urlopen(url) as response:
        if response.status != 200:
            print(f"Error: {response.status}")
            exit(-1)
        response_text = response.read().decode('utf-8')

    match = search(PATTERN, response_text)
    if not match:
        print("No data found.")
        return []

    yt_data = loads(match.group().lstrip("var ytInitialData =").rstrip(";</script>"))

    media_list = \
        yt_data["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"]["sectionListRenderer"]["contents"][0][
            "itemSectionRenderer"]["contents"]

    videos = [{
        "songId": media["videoRenderer"]["videoId"],
        "songName": media["videoRenderer"]["title"]["runs"][0]["text"],
        "artistName": media["videoRenderer"]["ownerText"]["runs"][0]["text"],
        "thumbnail": media["videoRenderer"]["thumbnail"]["thumbnails"][0]["url"],
        "youtubeUrl": f'https://youtu.be/{media["videoRenderer"]["videoId"]}'
    } for media in media_list if "videoRenderer" in media]

    return dumps(videos[:min(top_k, len(videos))])


if __name__ == '__main__':
    TOP = getenv("TOP_K", 1)
    print(yt_search(" ".join(argv[1]), TOP))
