import requests

def sendGet(url, payload = None):
    r = requests.get(url, payload)
    return r.json()


def sendPost(url, payload=None):
    r = requests.post(url, payload)
    return r.json()
