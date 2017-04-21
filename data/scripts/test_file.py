import pickle
from data.models import Comment, Author, Forum, ModelStorage, Accuracy

def run():

    print("Hello")

    #ModelStorage.objects.all().update(vectorizer = [11,2,3,4])
    #ModelStorage.objects.all().update(classifier = [52,5,3,4])
    #modelstorage.save()


    all = ModelStorage.objects.all().values_list("vectorizer", flat = True)[0]
    print(all)
    for i in all:
        print(i)

    print("---")

    all = ModelStorage.objects.all().values_list("classifier", flat = True)[0]
    print(all)
