import requests as reqs

from urllib import response
from urllib.parse import urlencode

API_KEY = "AIzaSyCk3plI3fFdjl8bc0ihdvFuJk8flqkcIHU"
PLACE_ID = ""

def get_from_name(name):
    response = reqs.get('https://maps.googleapis.com/maps/api/place/findplacefromtext/json?' + urlencode(
        {'input': name, 'inputtype': 'textquery', 'key': API_KEY}
    ))

    resp_info = response.json()

    if resp_info['status'] == 'OK':
        # print(resp_info['candidates'][0])
        datas = resp_info['candidates']
        for data in datas:
            get_review(data['place_id'])
    else:
        print(resp_info['status'], resp_info['error_message'])

def get_review(place_id):
    response = reqs.get(
        'https://maps.googleapis.com/maps/api/place/details/json?' + urlencode(
            {'place_id': place_id, 'key': API_KEY}))
    # Read response as json
    resp_details = response.json()
    # status=OK: the place was successfully detected and at least one result was returned
    for i in range(len(resp_details)):
        if resp_details['status'] == 'OK':
            print(resp_details)

get_from_name("ศาลาแก้วกู่@หนองคาย")