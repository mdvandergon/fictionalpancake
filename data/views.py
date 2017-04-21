import json
from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.http import HttpResponseRedirect, HttpResponse
from graphos.sources.model import ModelDataSource
from .models import Comment, Author, Forum
from .scripts.predict_class_user_input import run_classifier
from .forms import PredictForm

def index(request):
    context = {'nbar': 'home', 'form': PredictForm()}
    return render(request, 'index.html', context)

def stats(request):
    latest_comment_list = Comment.objects.order_by('-date_created')[:5]
    context = {'latest_comment_list': latest_comment_list, 'nbar': 'stats'}
    return render(request, 'stats.html', context)

class CommentDetail(DetailView):
    model = Comment
    template_name = "comment_detail.html"
    slug_url_kwarg = "comment_slug"
    def get_context_data(self, **kwargs):
        context = super(CommentDetail, self).get_context_data(**kwargs)
        return context

class JSONFormMixin(object):
    def create_response(self, vdict=dict(), valid_form=True):
        response = HttpResponse(json.dumps(vdict), content_type='application/json')
        response.status = 200 if valid_form else 500
        return response

class PredictFormBaseView(FormView):
    form_class = PredictForm

    def create_response(self, vdict=dict(), valid_form=True):
        response = HttpResponse(json.dumps(vdict), content_type='application/json')
        response.status = 200 if valid_form else 500
        return response

    def form_valid(self, form):
        text = form.data["text"]
        predicted_class = run_classifier(text)
        forum = Forum.objects.get(pk=predicted_class)
        ret = {"success": 1}
        ret["predicted_forum"] = forum.name
        return self.create_response(ret, True)

    def form_invalid(self, form):
        ret = {"success": 0, "form_errors": form.errors }
        return self.create_response(ret, False)

class PredictFormView(JSONFormMixin, PredictFormBaseView):
    # part of a design pattern to pass through to the BaseView
    pass

def TimeChart(request):
    forum_id = 1
    q = Comment.objects.raw(
        '''select name, extract(dow from date_posted) as dow, count(*), total_count, round(100.0 * count(*) /  total_count,1)  as percentage
             from data_comment
             join data_forum
                  on data_comment.forum_id = data_forum.id
             join
                  (select data_forum.id as tab_id, count(*) as total_count
                       from data_comment
                       join data_forum
                            on data_comment.forum_id = data_forum.id
                       group by data_forum.id) as total_ct_table
                  on total_ct_table.tab_id = data_comment.forum_id
             group by name, dow, total_count
             order by name, dow;''')
    data_source = ModelDataSource(q, fields=['name', 'dow', 'percentage'])

    # Chart object
    chart = LineChart(data_source)
    context = {'time_chart': chart}
    return render(request, 'stats.html', context)
