from django.conf.urls import include, url
from django.views.generic.base import RedirectView
from django.views.generic.edit import FormView
from django.contrib import admin
admin.autodiscover()
import data.views
from data.views import CommentDetail, PredictFormView

# Examples:
# url(r'^$', 'fictionalpancake.views.home', name='home'),
# url(r'^blog/', include('blog.urls')),

favicon_view = RedirectView.as_view(url='/static/favicon.ico', permanent=True)

urlpatterns = [
    url(r'^favicon\.ico$', favicon_view),
    url(r'^$', data.views.index, name='index'),
    url(r'^stats/', data.views.stats, name='stats'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^data/(?P<pk>[-\w]+)/$', CommentDetail.as_view(), name='comment_detail'),
    url(r'^predict/$', PredictFormView.as_view(), name='predict'),
    url(r'^django-rq/', include('django_rq.urls')),
]
