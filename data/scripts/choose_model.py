"""
Module that:
    Loads data
    Creates Train/Test sets
    Trains HashingVectorizer
    Runs models
    Stores best model and vectorizer to access to django
    Stores historical performance to database
"""
import re
import math
import random
import pandas as pd
import numpy as np
from textblob import TextBlob
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.linear_model import Perceptron
from sklearn.naive_bayes import MultinomialNB
from data.models import Comment, Author, Forum, ModelStorage, Accuracy


def get_num_comments():
    """
    Returns number of comments in database.
    """
    num_comments = Comment.objects.count()
    return num_comments


def get_data(offset, limit):
    """
    Gets comments and author data from database.
    In:
        - offset: SQL offset
        - limit: SQL limit
    Out:
        - pandas dataframe with columns 'outlet' and 'comment'
    """
    data = pd.DataFrame.from_records(Comment.objects.all().order_by('id').values('id', 'forum', 'clean_comment')[offset:limit])
    data["madeup_id"] = [i for i in range(offset, limit)]

    return data


def lemmatized_tokens_and_pos(comment):
    """
    Splits comment into lemmatized tokens and adds POS tags.
    http://stackoverflow.com/questions/1787110/what-is-the-true-difference-between-lemmatization-vs-stemming
    In:
        - comment (str)
    Out:
        - list of lemmatized tokens and POS tags
    """
    blob = TextBlob(comment)
    lemma_tokens = [word.lemma for word in blob.words]
    pos_list = [tag[1] for tag in blob.tags]

    return lemma_tokens + pos_list


def classify_comment(comment_list, vectorizer, detector):
    """
    Classifies comment.
    In:
        - comment_list: (lst) list of comments to classify
        - vectorizer: vectorizer instance
        - detector: classifier instance
    Out:
        - predicted class
    """
    comment_tfidf = vectorizer.transform(comment_list)
    return detector.predict(comment_tfidf)


def get_random_testset_indexes(num_comments, test_len = 10000):
    """
    Returns dict of indexes for training set.
    In:
        - num_comments: (int) number of comments in db
        - test_len: (int) number of test cases
    Out:
        - index_dict: (dict) with indexes as keys
    """
    index_dict = {}

    for i in range(test_len):
        current_ind = random.randint(0, num_comments)
        while current_ind in index_dict:
            current_ind = random.randint(0, num_comments)
        index_dict[current_ind] = None

    return index_dict


def run():
    '''
    Sets the classifiers and runs models, determining the highest-performing
    one.
    '''
    #defining classifiers to be trained; need to support partial fit
    classifiers = {
        'SGD': SGDClassifier(),
        'Perceptron': Perceptron(),
        'NBM': MultinomialNB(alpha=0.01)
    }

    vectorizer = HashingVectorizer(decode_error = 'ignore',
                                    n_features = 2 ** 18,
                                    analyzer = lemmatized_tokens_and_pos,
                                    non_negative = True,
                                    ngram_range = (2,3)
                                    )

    #We have 4 classes
    all_classes = np.array([1,2,3,4])

    batch_size = 40000
    test_len = 100000

    #for now, we hard-coded the number of comments to use, due to low-memory issues
    #we would otherwise run: num_comments = get_num_comments()
    num_comments = 2000000
    
    test_indexes = get_random_testset_indexes(num_comments, test_len)
    test_set = pd.DataFrame(columns=['id', 'forum', 'clean_comment', 'madeup_id'])

    epoq = 0
    required_epoqs = math.ceil(num_comments / batch_size)

    for offset in range(0, num_comments, batch_size):

        epoq += 1
        print("\n---- Starting epoq: {}/{}".format(epoq, required_epoqs))

        data = get_data(offset, offset + batch_size)

        #picking out data for final test
        test_set = test_set.append(data[data["madeup_id"].isin(list(test_indexes.keys()))])

        #removing rows that are now part of the test set.
        data = data[~data["madeup_id"].isin(list(test_indexes.keys()))]

        X_train, X_test, y_train, y_test = train_test_split(data.clean_comment, data.forum, test_size=0.05)

        print("Vectorizing comments")
        comment_vector = vectorizer.transform(X_train)
        comment_test_vector = vectorizer.transform(X_test)

        for classifier, cls in classifiers.items():
            print("\tTraining cls: ", classifier)
            cls.partial_fit(comment_vector, y_train, classes=all_classes)

            #performance on within-batch test
            accuracy = cls.score(comment_test_vector, y_test)
            print("\tClassifier {} achieves within batch accuracy of {}".format(classifier, accuracy))

    print("\nStarting testing.")

    print("How balanced is our test set?")
    print(test_set['forum'].value_counts())

    best_score = 0
    comment_test_vector = vectorizer.transform(test_set['clean_comment'])

    for classifier, cls in classifiers.items():
        accuracy = cls.score(comment_test_vector, test_set.forum)

        print("Classification report for cls: ", classifier)
        y_pred = cls.predict(comment_test_vector)
        print(classification_report(test_set.forum, y_pred))

        #Are doing partial_fit after scoring to further train cls
        #in case it will be the best performing
        cls.partial_fit(comment_test_vector, test_set.forum, classes=all_classes)

        print("Classifier {} achieves test score of {}".format(classifier, accuracy))
        if accuracy >= best_score:
            best_score = accuracy
            best_model = [classifier, cls]

        #storing achieved performance
        ml_model = Accuracy(model_type=classifier, score=accuracy, train_len=num_comments-test_len)
        ml_model.save()

    best_cls = best_model[1]
    print("Best CLS is: {}".format(best_model[0]))

    #Storing vectorizer and model in db
    ModelStorage.objects.all().update(vectorizer = vectorizer)
    ModelStorage.objects.all().update(classifier = best_cls)
    print("Wrote vectorizer and classifier to ModelStorage. Goodbye.")
