# This code is based on Steve Oney's example
from secret import app_ID, app_SECRET
from requests_oauthlib import OAuth2Session

import webbrowser
import json
from datetime import datetime
import csv

# for Eventbrite oAuth
APP_ID = app_ID
APP_SECRET = app_SECRET
AUTHORIZATION_BASE_URL = 'https://www.eventbrite.com/oauth/authorize'
TOKEN_URL = 'https://www.eventbrite.com/oauth/token'
REDIRECT_URI = 'https://www.programsinformationpeople.org/runestone/oauth'

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
eventbrite_session = False


def eventToCSV(filename, inputList, fieldnames):
    with open(filename, "w", newline="", encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in inputList:
            writer.writerow(
                {
                    "Name": item["name"]["text"],
                    "id": item["id"],
                    "Start": item["start"]["local"].replace(
                        "T",
                        " "),
                    "End": item["end"]["local"].replace(
                        "T",
                        " "),
                    "URL": item["url"],
                    "Free": item["is_free"]})


def make_eventbrite_request(url, params=None):
    # we use 'global' to tell python that we will be modifying this global
    # variable
    global eventbrite_session

    if not eventbrite_session:
        start_eventbrite_session()

    if not params:
        params = {}

    return eventbrite_session.get(url, params=params)


def start_eventbrite_session():
    global eventbrite_session

    # 0 - get token from cache
    try:
        token = get_saved_token()
    except FileNotFoundError:
        token = None

    if token:
        eventbrite_session = OAuth2Session(APP_ID, token=token)

    else:
        # 1 - session
        eventbrite_session = OAuth2Session(
            APP_ID, redirect_uri=REDIRECT_URI)

        # 2 - authorization
        authorization_url, state = eventbrite_session.authorization_url(
            AUTHORIZATION_BASE_URL)
        print('Opening browser to {} for authorization'.format(authorization_url))
        webbrowser.open(authorization_url)

        # 3 - token
        redirect_response = input('Paste the full redirect URL here: ')
        token = eventbrite_session.fetch_token(
            TOKEN_URL,
            client_secret=APP_SECRET,
            authorization_response=redirect_response.strip())

        # 4 - save token
        save_token(token)


def get_saved_token():
    with open('token.json', 'r') as f:
        token_json = f.read()
        token_dict = json.loads(token_json)

        return token_dict


def save_token(token_dict):
    with open('token.json', 'w') as f:
        token_json = json.dumps(token_dict)
        f.write(token_json)


# Cache system of events data

aa_events_dict = {}
cu_events_dict = {}
attend_dict = {}


def write_time_stamp(input, expire_in_days):
    input["time_stamp"] = datetime.now().strftime(DATETIME_FORMAT)
    input["expire_in_days"] = expire_in_days


def is_expired(input):
    now = datetime.now()
    time_stamp = datetime.strptime(input["time_stamp"], DATETIME_FORMAT)
    expire_in_days = input["expire_in_days"]
    delta = now - time_stamp
    delta_in_days = delta.days

    if delta_in_days > expire_in_days:
        return True
    else:
        return False

cu_params = {
    "sort_by": "date",
    "location.address": "Champaign",
    "location.within": "10mi",
    "page": 1}
aa_params = {
    "sort_by": "date",
    "location.address": "AnnArbor",
    "location.within": "10mi",
    "page": 1}


def prepare_data(filename, method, params):
    events_dict = {}
    try:
        with open(filename, 'r') as f:
            events_json = f.read()
            events_dict = json.loads(events_json)
            if is_expired(events_dict["pagination"]):
                raise FileNotFoundError

    except FileNotFoundError:
        response = make_eventbrite_request(
            'https://www.eventbriteapi.com/v3' + method,
            params)
        with open(filename, 'w') as f:
            events_dict = json.loads(response.text)
            write_time_stamp(events_dict["pagination"], 2)
            f.write(json.dumps(events_dict))
    return events_dict

aa_events_dict = prepare_data("aa_events.json", "/events/search/", aa_params)
cu_events_dict = prepare_data("cu_events.json", "/events/search/", cu_params)


eventToCSV("aa_events.csv", aa_events_dict["events"], [
           "Name", "id", "Start", "End", "URL", "Free"])
eventToCSV("cu_events.csv", cu_events_dict["events"], [
           "Name", "id", "Start", "End", "URL", "Free"])
