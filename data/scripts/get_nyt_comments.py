"""
Module that gets comments from NYTimes Community API for a date.

Example usage:

    python manage.py runscript get_nyt_comments --script-args $NYT1

    where:
       - $NYT1 is a NYT API key stored as environment variable

Requirements:
    - Set api key values in environment
"""
import sys
import json
import urllib.request
import time
from django.conf import settings
from datetime import date, datetime
from .write_comment import write_comment
from .comment import Comment

from data.models import Progress

def get_next_day(in_date):
    """
    Returns the next day's date as str of format YYYYMMDD if not today's
    date. Then returns None.
    In:
        - in_date: (str) of format "YYYYMMDD"
    Out:
        - next day's date of format "YYYYMMDD" or None
    """
    new_date = datetime.fromordinal(datetime.strptime(in_date, '%Y%m%d').date().toordinal() + 1)

    if new_date.date() == date.today():
        return None

    return str(new_date.year) + str(new_date.month).zfill(2) + str(new_date.day).zfill(2)


def get_nyt_comments(public_api_key, date, offset = 0):
    """
    Gets NYT comments for date and writes them to DB.
    In:
        - public_api_key: (str) public api key for NYT API
        - date: (str) date of format YYYYMMDD
        - offset: (int) offset for retrieval of comments,
                    e.g., 1 would indicate to start with
                    second comment
    """
    #initializing totalComments to high value
    totalComments = 1000000

    while offset < totalComments:
        base_url = "https://api.nytimes.com/svc/community/v3/user-content/by-date.json"
        req_url = base_url + "?api-key=" + public_api_key + "&date=" + date + "&offset=" + str(offset)

        try:
            with urllib.request.urlopen(req_url) as f:
                response_as_str = f.read().decode('utf-8')
                json_response = json.loads(response_as_str)

                totalComments = int(json_response['results']['totalCommentsFound'])

                for comment in json_response["results"]["comments"]:

                    userDisplayName = comment["userDisplayName"]
                    userID = comment["userID"]
                    userLocation = comment["userLocation"]
                    commentID = comment["commentID"]
                    commentBody = comment["commentBody"]
                    createDate = str(datetime.fromtimestamp(int(comment["createDate"])))
                    recommendationCount = comment["recommendationCount"]
                    comment_tuple = ("NYT", userDisplayName, userID, userLocation, commentID,
                                    commentBody, createDate, recommendationCount)

                    # create object and write
                    comment = Comment(comment_tuple)
                    comment_dict = comment.as_dict()
                    write_comment(comment_dict)

        except urllib.error.HTTPError as err:
            if err.code == 504:
                print("Got 504 error. Sleeping for ten seconds, then trying again.")
                time.sleep(10)
                offset -= 25
            elif err.code == 429:
                print("Got 429 error. Probably reached max requests limit.")
                print("We will store progress and come back to this offset tomorrow.")
                break
            else:
                print("Got an error:")
                print(err)
                raise

        #increase offset by 25 as API returns 25 comments with each request
        offset += 25
        progress_string = ",".join((date, str(offset), str(offset >= totalComments)))

        progress, created = Progress.objects.update_or_create(forum = "NYT", defaults={"progress": progress_string})

        #only allowed 5 requests per second; going for 4
        time.sleep(0.25)


def run(*args):
    start_time = time.time()
    print("Starting NYT comment colletion.")
    public_api_key = args[0]

    #Handling progress
    if Progress.objects.filter(forum="NYT").exists():
        print("Forum entry exists. Retrieving progress")
        progress = Progress.objects.filter(forum__exact = 'NYT').values_list("progress", flat = True)
        print("Found progress: ", progress)
        prev_date, offset, finished = progress[0].split(",")
        offset = int(offset)
    else:
        #No progress found. Forum was not worked on before.
        #Starting at our start date of 20160601.
        prev_date = "20160601"
        offset = 0
        finished = False

    if finished == "True":

        next_date = get_next_day(prev_date)

        if next_date:
            comments = get_nyt_comments(public_api_key, next_date)

        else:
            #We don't want to get today's comments in case more comments will be
            #written later on.
            print("Supposed to get comments from today, but will do that tomorrow.")
            sys.exit()

    else:
        comments = get_nyt_comments(public_api_key, prev_date, offset)

    print("-- DONE --")
    print("-- {} s --".format(time.time() - start_time))
