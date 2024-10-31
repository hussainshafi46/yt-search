import re
import json
import requests
from requests.utils import requote_uri

PATTERN = r'var ytInitialData =(.+)"targetId":"search-page"};</script>'


def search(query, top_k=1):
    url = f"https://www.youtube.com/results?search_query={requote_uri(query)}"

    response = requests.get(url)
    if response.status_code != 200:
        print(response)
        exit(-1)

    yt_data = json.loads(re.search(PATTERN, response.text).group().lstrip("var ytInitialData =").rstrip(";</script>"))

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

    return videos[:min(top_k, len(videos))]