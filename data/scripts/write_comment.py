"""
Module that writes comment dictionaries to database
    Input:
    comment_dict = {
        "forum"
        "author"
        "api_author_id"
        "location"
        "date_added"
        "date_posted"
        "api_comment_id"
        "raw_comment"
        "clean_comment"
        "asset_url"
        "likes"
        "num_bold" }
"""
from data.models import Comment, Author, Forum
from django.utils.dateparse import parse_datetime
from django.db import IntegrityError
import pytz


TIME_ZONE = 'UTC'

def write_comment(d):
    # get/create news forum
    forum, o_created = Forum.objects.get_or_create(name = d["forum"])

    # get/create author
    author, a_created = Author.objects.get_or_create(
        api_author_id=d["api_author_id"],
        forum=forum,
        defaults={'name': d["author"], 'location': d["location"]})

    # replacing keys so that we can pass the rest of the dict to model and save
    d["forum"] = forum
    d["author"] = author

    # Naive to aware date
    naive = parse_datetime(d["date_posted"])
    d["date_posted"] = pytz.timezone(TIME_ZONE).localize(naive)

    try:
        comment_id, comment_created = Comment.objects.get_or_create(
            api_comment_id = d["api_comment_id"], forum = d["forum"],
            defaults = {'date_posted': d["date_posted"],
                        'raw_comment': d['raw_comment'],
                        'clean_comment': d['clean_comment'],
                        'asset_url': d['asset_url'],
                        'likes': d['likes'],
                        'num_bold': d['num_bold'],
                        'num_uppercase': d['num_uppercase'],
                        'author': d['author']})
    except IntegrityError as e:
            print("Got an integrity error {} \n when working with dict: {}".format(e.__cause__, d))
    except:
        print("Got another error when working with dict: {}".format(d))
        raise
