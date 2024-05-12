from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'home.html')

def back(request):
    return render(request, 'blog-details.html')