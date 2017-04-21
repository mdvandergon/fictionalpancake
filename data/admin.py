from django.contrib import admin
from .models import *

admin.site.register(Comment)
admin.site.register(Author)
admin.site.register(Forum)
admin.site.register(Progress)
admin.site.register(Accuracy)
admin.site.register(ModelStorage)
