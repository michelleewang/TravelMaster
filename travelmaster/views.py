from django.shortcuts import render
from django.views import generic
import os
from google.cloud import vision
from google.cloud.vision import types
from google.cloud import translate_v2 as translate
import googlemaps
import time
import urllib.request
import json
import re

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/Users/michellewang/Desktop/TravelMaster/ServiceAccountToken.json"

# Translation API
translate_client = translate.Client()
languageList = translate_client.get_languages() # complete list of languages from google translate

# Directions API
keyFile = open("/Users/michellewang/Desktop/TravelMaster/API_key.txt","r")
key = keyFile.read()

# Vision API
vision_client = vision.ImageAnnotatorClient()

# homepage
def home(request):
    return render(request, 'home.html', {})

# translate text using translate API
def translation(request):

    og_text = request.POST.get('og_text', '')
    t_lang = request.POST.get('target_lang', '')
    error_message = "No Translation."

    if (og_text != '') or (t_lang != ''):

        # get target language
        for lang in languageList:
            if lang['name'].lower() == t_lang.lower():
                target = lang['language']
                target_lang = lang['name']

                # translate
                result = translate_client.translate(og_text, target)
                translation = result['translatedText']

                # get original language
                detectedLang = result['detectedSourceLanguage']
                for lang in languageList:
                    if lang['language'].lower() == detectedLang.lower():
                        og_lang = lang['name']

                return render(request, 'translation.html', {'og_lang':og_lang, 'target_lang':target_lang, 'translation':translation})

    return render(request, 'translation.html', {'error_message':error_message})

def cleanhtml(text):
    cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    cleantext = re.sub(cleanr, ' ', text)
    return cleantext

# get direction using directions API
def navigation(request):

    origin = request.POST.get('origin', '').replace(' ', '+')
    destination = request.POST.get('destination', '').replace(' ', '+')
    error_message = "Unable to get directions."

    if (origin != '') or (destination != ''):
        endpoint = 'https://maps.googleapis.com/maps/api/directions/json?'
        nav_request = endpoint+'origin='+origin+'&destination='+destination+'&key='+key
        directions = json.loads(urllib.request.urlopen(nav_request).read())
        steps = []

        for step in directions['routes'][0]['legs'][0]['steps']:
            steps.append(cleanhtml(step['html_instructions']))

        print(steps)
        return render(request, 'navigation.html', {'steps':steps})
    return render(request, 'navigation.html', {'error_message':error_message})

# image analysis homepage
def images(request):
    return render(request, 'images.html', {})

# detect text from image using vision API
def detectText(request):

    img_url = request.POST.get('img_url', ' ')
    image = vision.types.Image()
    image.source.image_uri = img_url
    response = vision_client.document_text_detection(image=image)
    text = response.full_text_annotation.text

    return render(request, 'detectText.html', {'img_url':img_url, 'text':text})

# detect landmark from image using vision API
def detectLandmark(request):

    img_url = request.POST.get('img_url', ' ')
    image = vision.types.Image()
    image.source.image_uri = img_url
    response = vision_client.landmark_detection(image=image)
    landmarks = response.landmark_annotations
    landmarkList = []

    for landmark in landmarks:
        landmarkList.append(landmark.description)

    return render(request, 'detectLandmark.html', {'img_url':img_url, 'landmarks':landmarkList})

# detect faces from image using vision API
def detectFaces(request):

    img_url = request.POST.get('img_url', ' ')
    image = vision.types.Image()
    image.source.image_uri = img_url
    response = vision_client.face_detection(image=image)
    faceAnnotations = response.face_annotations

    likelihood = ('Unknown', 'Very Unlikely', 'Unlikely', 'Possibly', 'Likely', 'Very Likely')

    faces = []

    for face in faceAnnotations:
        emotions = []
        emotions.append('Joy likelyhood: {0}'.format(likelihood[face.joy_likelihood]))
        emotions.append('Sorrow likelyhood: {0}'.format(likelihood[face.sorrow_likelihood]))
        emotions.append('Anger likelyhood: {0}'.format(likelihood[face.anger_likelihood]))
        emotions.append('Surprise likelyhood: {0}'.format(likelihood[face.surprise_likelihood]))
        emotions.append('Headwear likelyhood: {0}'.format(likelihood[face.headwear_likelihood]))
        faces.append(emotions)

    numFaces = len(faces)

    return render(request, 'detectFaces.html', {'img_url':img_url, 'faces':faces, 'numFaces':numFaces})
