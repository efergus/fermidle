
import requests

URL = "https://en.wikipedia.org/w/api.php"

def image_search(thing: str):
    session = requests.session()

    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srlimit": 3,
        "srsearch": thing
    }

    try:
        response = session.get(url=URL, params=params)
        data = response.json()
        results = data['query']['search']
        pageids = [str(result['pageid']) for result in results]

        data = {}
        for pageid in pageids:
            params = {
                "action": "query",
                "format": "json",
                "prop": "pageimages|info",
                "pithumbsize": 400,
                "pilimit": 2,
                "pageids": pageid,
                "inprop": "url"
            }
            response = session.get(url=URL, params=params)
            data = response.json()
            page = data["query"]["pages"][pageid]
            if "thumbnail" in page:
                return page["thumbnail"]["source"]
    except Exception as e:
        print(e)
        return
