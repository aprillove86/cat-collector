from django.shortcuts import render, redirect
from .models import Cat, Toy, Photo
import boto3
import uuid
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .forms import FeedingForm
##fake database to follow

S3_BASE_URL = 'https://s3.us-east-1.amazonaws.com/'
BUCKET = 'catfan-bucket'

# Create your views here.
def home(request):
    return render(request, 'home.html')
def about(request):
    return render(request, 'about.html')
def cats_index(request):
    cats = Cat.objects.all()
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


class CatCreate(CreateView):
    model = Cat
    fields = '__all__'
class ToyCreate(CreateView):
    model = Toy
    fields = '__all__'

    # fat models, skinny controllers

class CatUpdate(UpdateView):
    model = Cat
    fields = ('name', 'breed', 'description', 'age')
class ToyUpdate(UpdateView):
    model = Toy
    fields = ('name', 'color')


class CatDelete(DeleteView):
    model = Cat
    success_url ='/cats/'
class ToyDelete(DeleteView):
    model = Toy
    success_url ='/toys/'
