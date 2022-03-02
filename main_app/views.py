from django.shortcuts import render, redirect
from .models import Cat, Toy, Photo
import boto3
import uuid
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .forms import FeedingForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
##fake database to follow

S3_BASE_URL = 'https://s3.us-east-1.amazonaws.com/'
BUCKET = 'catfan-bucket'

# Create your views here.
def home(request):
    return render(request, 'home.html')
def about(request):
    return render(request, 'about.html')

@login_required
def cats_index(request):
    cats = Cat.objects.filter(user = request.user)
    return render(request, 'cats/index.html', {'cats': cats})
def toys_index(request):
    toys = Toy.objects.all()
    return render(request, 'toys/index.html', {'toys': toys})


def cats_detail(request, cat_id):
   cat = Cat.objects.get(id=cat_id)
   feeding_form = FeedingForm()
   
   toys_cat_doesnt_have = Toy.objects.exclude(id__in = cat.toys.all().values_list('id'))

   return render(request, 'cats/detail.html',
   {'cat': cat, 
   'feeding_form': feeding_form,
   'toys': toys_cat_doesnt_have
    })

def add_feeding(request, cat_id):
    form = FeedingForm(request.POST)
    if form.is_valid():
        new_feeding = form.save(commit=False) 
        new_feeding.cat_id = cat_id
        new_feeding.save()
    return redirect('detail', cat_id=cat_id)

def toys_detail(request, toy_id):
   toy = Toy.objects.get(id=toy_id)
   return render(request, 'toys/detail.html', {'toy': toy })

def assoc_toy(request, cat_id, toy_id):
   Cat.objects.get(id=cat_id).toys.add(toy_id)
   return redirect('detail', cat_id=cat_id)

def add_photo(request, cat_id):
    photo_file = request.FILES.get('photo-file')
    if photo_file:
        s3 = boto3.client('s3')
        key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
        try:
            s3.upload_fileobj(photo_file, BUCKET, key)
            url = f'{S3_BASE_URL}{BUCKET}/{key}'
            photo = Photo(url=url, cat_id=cat_id)
            photo.save()

        except Exception as error:
            print('*********************')
            print('An error occuured while uploading to S3')
            print(error)
            print('*********************')
    return redirect('detail', cat_id=cat_id)

def signup(request):
    error_message = ''
    if request.method == 'POST':

        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
        else:
            error_message = 'invalid sign up- please try again'

    form = UserCreationForm()
    context = {'form': form, 'error_message': error_message }
    return render(request, 'registration/signup.html', context)


class CatCreate(LoginRequiredMixin, CreateView):
    model = Cat
    fields = ('name', 'breed', 'age', 'description')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class ToyCreate(LoginRequiredMixin, CreateView):
    model = Toy
    fields = '__all__'

    # fat models, skinny controllers

class CatUpdate(LoginRequiredMixin, UpdateView):
    model = Cat
    fields = ('name', 'breed', 'description', 'age')
class ToyUpdate(LoginRequiredMixin, UpdateView):
    model = Toy
    fields = ('name', 'color')


class CatDelete(LoginRequiredMixin, DeleteView):
    model = Cat
    success_url ='/cats/'
class ToyDelete(LoginRequiredMixin, DeleteView):
    model = Toy
    success_url ='/toys/'
