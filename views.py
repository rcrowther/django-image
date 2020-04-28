from django.shortcuts import render

# Create your views here.
from django.views.generic.edit import CreateView
from image.models import Reform


class ReformCreate(CreateView):
    model = Reform
    fields = ['filter_spec', 'width', 'height']
