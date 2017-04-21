"""
Script that loads best model and makes predictions.
"""
from data.models import ModelStorage
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.linear_model import Perceptron
from sklearn.naive_bayes import MultinomialNB


def load_models():
    """
    Loads vectorizer and classifier.
    In:
        -
    Out:
        - vectorizer, classifier
    """
    vectorizer = ModelStorage.objects.all().values_list("vectorizer", flat = True)[0]
    classifier = ModelStorage.objects.all().values_list("classifier", flat = True)[0]

    return vectorizer, classifier


def classify_comment(comment, vectorizer, classifier):
    """
    Classifies comment.
    In:
        - comment: (str)
        - vectorizer: HashingVectorizer instance
        - classifier: Classifier instance
    Out:
        - predicted class
    """
    vec_comment = vectorizer.transform(comment)
    pred_class = classifier.predict(vec_comment)
    #Perceptron does not calc probabilities; therefore, can't
    #output predict_proba
    #prob_each_class = classifier.predict_proba(vec_comment)

    return pred_class[0]

def run_classifier(string):

    vectorizer, classifier = load_models()
    pred_class = classify_comment([string], vectorizer, classifier)

    return pred_class
