"""
Module that gets comments from disqus API for a list
of news-sites (forums).

Example usage:

    python manage.py runscript get_disqus_comments -script-args $DISQUS1 1000 newssite

    where:
       - $DISQUS1 is a environment variable
       - 1000 is number of requests with 100 comments each
       - newssite is forum which comments shall be collected.

Requirements:
    - Set api key values in environment
    - disqusapi module as found on Github. Can be installed via:
    'pip3 install git+git://github.com/disqus/disqus-python.git'
"""

import json
import sys
import time
from disqusapi import DisqusAPI
from .write_comment import write_comment
from .comment import Comment
from data.models import Progress

def get_disqus_comments(public_api_key, forum, max_requests = 1000, next_cursor = None):
    """
    Gets disqus comments for forum and writes them to DB.
    In:
        - public_api_key: (str) public api key for disqus API
        - forum: (str) a disqus forum, e.g., 'breibartproduction'
        - max_requests: (int) number of API requests to make max
        - next_cursor: (str) next cursor for pagination (optional)
    """
    request_counter = 0
    has_next = True

    disqus = DisqusAPI(public_key = public_api_key)

    while request_counter < max_requests and has_next:

        #in case we want to continue where we left off.
        if next_cursor:
            response = disqus.get('posts/list', method = "GET", version ='3.0', forum = forum,
                                    limit = 100, since = "2016-06-01T00:00:00", order = "asc",
                                    cursor = next_cursor)
        else:
            response = disqus.get('posts/list', method = "GET", version ='3.0', forum = forum,
                                    limit = 100, since = "2016-06-01T00:00:00", order = "asc")

        #if there is no further page left, we don't need to make another request
        if response.cursor["hasNext"]:
            next_cursor = response.cursor["next"]
        else:
            has_next = False

        #getting content of comments
        list_of_posts = response.response

        for post in list_of_posts:

            try:
                author = post['author']['name']
                author_id = post['author']['id']
                author_location = post['author']['location']
                comment_id = post['id']
                raw_comment = post['raw_message']
                likes = post['likes']
                time_created = post['createdAt']
                comment_tuple = (forum, author, author_id, author_location, comment_id,
                                    raw_comment, time_created, likes)

                # create object and write
                comment = Comment(comment_tuple)
                comment_dict = comment.as_dict()
                write_comment(comment_dict)

            except:
                #we were not able to get all attributes and will ignore this comment
                continue

        request_counter += 1
        progress, created = Progress.objects.update_or_create(forum = forum, defaults={"progress": next_cursor})


def run(*args):
    start_time = time.time()
    print("Starting Disqus comment collection.")

    public_api_key = args[0]
    max_requests = int(args[1])
    assert max_requests <= 1000, "Sorry. Can't make more than 1000 requests per hour."

    news_site = args[2]

    # Handling progress
    if Progress.objects.filter(forum = news_site).exists():
        print("Forum entry exists. Retrieving progress")
        progress = Progress.objects.filter(forum__exact = news_site).values_list("progress", flat = True)
        print("Found progress: ", progress)
        next_cursor = progress[0]
    else:
        next_cursor = "False"

    if next_cursor != "False":
        comments = get_disqus_comments(public_api_key, news_site, max_requests, next_cursor)
    else:
        comments = get_disqus_comments(public_api_key, news_site, max_requests)

    print("-- DONE --")
    print("-- {} s --".format(time.time() - start_time))
