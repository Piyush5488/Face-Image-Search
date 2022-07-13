import pytest
import psycopg2
import requests
import json

host = "localhost"
database="faceimage"
user="postgres"
password="qwerty"


def test_add_face():
    url = "http://127.0.0.1:8000/add_face/"
    with open('Test-Files/Joe-Biden.jpg', 'rb') as f:
        response = requests.post(url, files={"image":("Joe-Biden", f ,"Test-Files/Joe-Biden.jpg")})
        jsonFile = json.loads(response.text)
        assert jsonFile['body'] == "Image Successfully Added To The Database"


def test_add_metadeta():
    url = "http://127.0.0.1:8000/add_metadata/"
    # The ID you providing must already be present in the database
    data = {'id' : '1', 'name' : 'Joe Biden','date' : '09-03-2022','location' : 'Washington DC'}
    response = requests.post(url,data=data)
    jsonFile = json.loads(response.text)
    assert jsonFile['body'] == "Metadata Updated Successfully"
    return

def test_get_face_info():
    url = "http://127.0.0.1:8000/get_face_info/"
    # The ID you providing must already be present in the database
    data = {'face_id': '1'}
    response = requests.post(url, data=data)
    jsonFile = json.loads(response.text)
    assert jsonFile['body']['match'] == "{ id : 1, Name : Joe Biden, Date : 09-03-2022, Location : Washington DC }"
    return

def test_add_faces_in_bulk():
    url = "http://127.0.0.1:8000/add_faces_in_bulk/"
    with open('Test-Files/Bulk.zip', 'rb') as f:
        response = requests.post(url, files={"file":("faceImage.zip", f ,"Test-Files/Bulk.zip")})
        jsonFile = json.loads(response.text)
        assert jsonFile['body'] == "Images Successfully Added To The Database"
    return

def test_search_faces():
    url = "http://127.0.0.1:8000/search_faces/"
    with open('Test-Files/Narendra Modi 2.jpg', 'rb') as f:
        response = requests.post(url, data={'k' : '3','strictness' : '0.4'}, files={"image":("Narendra Modi", f ,"Test-Files/Narendra Modi 2.jpg")})
        jsonFile = json.loads(response.text)
        assert jsonFile['body']['matches'][0] == "{ id : 5, Name : Narendra Modi.jpg, Date : , Location :  }"
    return
