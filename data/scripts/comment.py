# CS 122: Fictional Pancakes Project
#
# Comment Cleaning and Feature Tracking
import re
from urllib.parse import urlparse

class Comment(object):
    '''
    Class to handle comment cleaning. Prepares comments
    for storage in db.
    '''

    def __init__(self, comment):
        '''
        Takes as input a comment (tuple)
        comment_tuple = (forum, author,
            author_id, author_location, comment_id,
            raw_comment, time_created, likes)
        '''
        self.comment = comment
        self.comment_dict = self.load_comment_dict()
        self.clean_comment = self.clean_comment()
        self.bold_count = self.count_bold()
        self.upper_count = self.count_upper()


    def load_comment_dict(self):
        return {
            "forum": self.comment[0],
            "author": self.comment[1],
            "api_author_id": self.comment[2],
            "location": self.comment[3],
            "api_comment_id": self.comment[4],
            "raw_comment": self.comment[5],
            "date_posted": self.comment[6],
            "likes": int(self.comment[7]),
            "clean_comment": None,
            "asset_url": None,
            "num_bold": None,
            "num_uppercase": None}

    def count_bold(self):
        '''
        Counts bold phrases.
        '''
        bold_count = self.comment_dict['raw_comment'].count("<b>")
        self.comment_dict['num_bold'] = bold_count

        return bold_count

    def as_dict(self):
        return self.comment_dict

    def keep_only_base_url(self, in_string):
        """
        Removes hrefs and only keeps domain.
        In:
            - in_string: (str) like comment
        Out:
            - (str)
        """
        search = '<a href="'
        len_search = len(search)
        begin_href = in_string.find(search)

        while begin_href > 0:

            end_link = in_string.find('"', begin_href + len_search + 1)
            if "<\x07>" in in_string:
                end_href = in_string.find('<\x07>', begin_href) + len("<\x07>")
            elif "<\a>" in in_string:
                end_href = in_string.find('<\a>', begin_href) + len("<\a>")
            else:
                return in_string

            parsed_url = urlparse(in_string[begin_href + len_search:end_link])
            domain = '{uri.netloc}'.format(uri=parsed_url)
            domain = re.sub(r'www\.|\.com|\.org', '', domain)

            in_string = in_string[:begin_href] + domain + in_string[end_href:]
            begin_href = in_string.find(search)

        return in_string

    def clean_comment(self):
        '''
        Keeps domains from links, strips html tags and extra spacing
        '''
        dirty_string = self.comment_dict['raw_comment']
        dirty_string = self.keep_only_base_url(dirty_string)

        regex = re.compile(r'(<.*?>)|([^a-zA-Z0-9])')
        clean_comment = regex.sub(' ', dirty_string)
        regex = re.compile(r'\s+')
        clean_comment = regex.sub(' ', clean_comment)

        self.comment_dict['clean_comment'] = clean_comment
        return clean_comment

    def count_upper(self):
        '''
        Counts the number of words in the comment that are
        all uppercase and are two letters or more in length
        '''
        comment_string = self.comment_dict['clean_comment']
        words = comment_string.split()

        upper_count = 0
        for word in words:
            if word.upper() == word and (len(word) > 1):
                upper_count += 1

        self.comment_dict['num_uppercase'] = upper_count
        return upper_count
