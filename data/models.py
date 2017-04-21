from django.db import models
from picklefield.fields import PickledObjectField

class Forum(models.Model):
    name = models.TextField()
    homepage = models.URLField()

class Author(models.Model):
    name = models.TextField()
    api_author_id = models.CharField(max_length=10000000)
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE)
    location = models.TextField(null=True)
    class Meta:
      unique_together = (("api_author_id", "forum"),)

class Comment(models.Model):
    api_comment_id = models.CharField(max_length=10000000)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_posted = models.DateTimeField()
    raw_comment = models.TextField()
    clean_comment = models.TextField()
    asset_url = models.URLField(blank=True, null=True)
    likes = models.IntegerField()
    num_bold = models.IntegerField()
    num_uppercase = models.IntegerField()
    class Meta:
      unique_together = (("api_comment_id", "forum"),)

# class to store progress from API querying
class Progress(models.Model):
    forum = models.TextField(primary_key = True)
    progress = models.TextField()

#class for accuracy over time
class Accuracy(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    model_type = models.TextField()
    score = models.DecimalField(max_digits=5, decimal_places=5)
    train_len = models.IntegerField()

#class for model storage
class ModelStorage(models.Model):
    vectorizer = PickledObjectField()
    classifier = PickledObjectField()
    vectorizer_needed = models.TextField(null=True)
