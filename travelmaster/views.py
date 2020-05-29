from django.shortcuts import render
from django.views import generic
import os
from google.cloud import vision
from google.cloud.vision import types
from google.cloud import translate_v2 as translate
import googlemaps
import time

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/Users/michellewang/Desktop/TravelMaster/ServiceAccountToken.json"
vision_client = vision.ImageAnnotatorClient()
translate_client = translate.Client()

# complete list of languages from google translate
languageList = translate_client.get_languages()

def home(request):
    return render(request, 'home.html', {})

def images(request):
    return render(request, 'images.html', {})

def translation(request):
    return render(request, 'translation.html', {})

def navigation(request):
    return render(request, 'navigation.html', {})

# detect test from image using vision API
def detectText(request):

    img_url = request.POST.get('img_url', ' ')
    image = vision.types.Image()
    image.source.image_uri = img_url
    response = vision_client.document_text_detection(image=image)
    text = response.full_text_annotation.text

    return render(request, 'detectText.html', {'img_url': img_url, 'text': text})

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

    return render(request, 'detectLandmark.html', {'img_url': img_url, 'landmarks': landmarkList})

# detect test from image using vision API
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

    return render(request, 'detectFaces.html', {'img_url': img_url, 'faces': faces, 'numFaces':numFaces})

# translate text using translate API
def translation(request):

    error_message = "No Translation."

    if request.POST.get('og_text', ' ') != ' ':

        og_text = request.POST.get('og_text', ' ')
        t_lang = request.POST.get('target_lang', ' ')

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
