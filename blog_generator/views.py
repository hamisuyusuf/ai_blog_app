from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
import json
from pytube import YouTube
import os 
import assemblyai as aai
import openai

# Create your views here.
@login_required
def home(request):
    return render(request, 'home.html')

@csrf_exempt
def generate_blog(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            yt_link = data['link']
            
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid data method'}, status=400)
        
        # Get the Youtube  title
        title = yt_title(yt_link)

        # Get transcript
        transcription = get_transcription(yt_link)
        if not transcription:
            return JsonResponse({'error': " Failed to get transcript"}, status=500)

        # Use OpenAI to generate_blog
        blog_content = generate_blog_from_transcription(transcription)
        if not blog_content:
            return JsonResponse({'error': " Failed to generate transcript "}, status=500)
        
        # Save the generated_blog to DB

        # return blog article as a response 
        return JsonResponse({'content': blog_content})

    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

def yt_title(link):
    yt = YouTube(link)
    title = yt.title
    return title

def  download_audio(link):
    yt = YouTube(link)
    video = yt.streams.filter(only_audio=True).first()
    out_file = video.download(output_path=settings.MEDIA_ROOT)
    base, ext = os.path.splitext(out_file)
    new_file = base + '.mp3'
    os.rename(out_file, new_file)
    return new_file

def get_transcription(link):
    audio_file = download_audio(link)

    aai.settings.api_key = "db31c1331d1f4e42a157df56ecacd095"
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file)

    # transcript = transcriber.transcribe("https://storage.googleapis.com/aai-web-samples/news.mp4")
    # # transcript = transcriber.transcribe("./my-local-audio-file.wav")

    return transcript.text

def generate_blog_from_transcription(transcription):
    openai.api_key = "sk-proj-pzaQhlNT65z1FReAxxLlT3BlbkFJfHyGRwWEA7HfCRv7YmJn"

    prompt = f"Based on the following transcript from a youtube video, i want you to write a comprhensive blog article, write it based on the transcript, but dont make it look like a youtube video, make it look like a proper blog article:\n\n{transcription}\n\nArticle:"

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=1000
    )

    generate_content = response.choices[0].text.strip()

    return generate_content 


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            error_message = "Invalid username or password"
            return render(request, 'login.html', {'error_message':error_message})

    return render(request, 'login.html')

def user_signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        repeatpassword = request.POST['repeatpassword']

        if password == repeatpassword:
            try:
                user = User.objects.create_user(username, email, password)
                user.save()
                login(request, user)
                return redirect('/')
            except:
                error_message = 'Error creatinf account'
            return render(request, 'signup.html', {'error_message':error_message})
        else:
            error_message = 'Password do not match'
            return render(request, 'signup.html', {'error_message':error_message})
    return render(request, 'signup.html')

def user_logout(request):
    logout(request)
    return redirect('/')