import os
from fastapi import FastAPI, File, UploadFile, Form
import psycopg2
from zipfile import ZipFile
import face_recognition

app = FastAPI()

host = "localhost"
database="faceimage"
user="postgres"
password="qwerty"

@app.post("/add_metadata")
async def add_metadata(id: str = Form(...),name: str = Form(...),date: str = Form(...),location: str = Form(...)):

    # connect to the db
    con = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password)

    # cursor
    cur = con.cursor()

    cur.execute("Update face_images set name = '"+name+"', date = '"+date+"', location = '"+location+"' Where id = "+id)

    # commit the transaction
    con.commit()

    # close the cursor
    cur.close()

    # close the connection
    con.close()

    return {"status": "OK", "body": "Metadata Updated Successfully"}


@app.post("/search_faces/")
async def search_faces(image: UploadFile = File(..., description = "An image file, possible containing multiple human faces."),
                       strictness: str = Form(...),
                       k: str = Form(...)):

    strictness = float(strictness)
    k = int(k)
    file_name = os.getcwd() + "/temp.jpg"
    with open(file_name, 'wb+') as f:
        f.write(image.file.read())
        f.close()

    # connect to the db
    con = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password)

    # cursor
    cur = con.cursor()

    # execute query
    cur.execute("select * from face_images")

    rows = cur.fetchall()

    known_encodings = []

    for r in sorted(rows):
        known_image = face_recognition.load_image_file(r[4])
        known_image_encoding = face_recognition.face_encodings(known_image)[0]
        known_encodings.append(known_image_encoding)

    image_to_test = face_recognition.load_image_file("temp.jpg")
    image_to_test_encoding = face_recognition.face_encodings(image_to_test)[0]

    face_distances = face_recognition.face_distance(known_encodings, image_to_test_encoding)
    face_distances_with_id = []
    response = []
    print(face_distances)
    for i in range(len(face_distances)):
        if(face_distances[i] <= strictness):
            face_distances_with_id.append((face_distances[i],i+1))


    face_distances_with_id.sort()
    length = min(len(face_distances_with_id),k)
    face_distances_with_id = face_distances_with_id[0:length]

    for i in range(length):
        cur.execute("select * from face_images where id = " + str(face_distances_with_id[i][1]))
        rows = cur.fetchall()
        temp = "{ "
        for r in rows:
            temp += f"id : {r[0]}, Name : {r[1]}, Date : {r[2]}, Location : {r[3]}"
        temp += " }"
        response.append(temp)

    print(face_distances_with_id)

    # close the cursor
    cur.close()

    # close the connection
    con.close()

    return {"status": "OK", "body": {"matches": response}}

@app.post("/add_face/")
async def add_face(image: UploadFile = File(..., description="An image file having a single human face.")):

    try:
        os.mkdir("Images")
        print(os.getcwd())
    except Exception as e:
        print(e)
    file_name = os.getcwd()+"/Images/"+image.filename.replace(" ", "-")
    with open(file_name,'wb+') as f:
        f.write(image.file.read())
        f.close()


    # connect to the db
    con = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password)

    # cursor
    cur = con.cursor()

    cur.execute("insert into face_images(name,date,location,imageUrl) values('"+image.filename+"','','','"+file_name+"')")

    # commit the transcation
    con.commit()

    # close the cursor
    cur.close()

    # close the connection
    con.close()

    return {"status": "OK", "body": "Image Successfully Added To The Database"}

@app.post("/add_faces_in_bulk/")
async def add_faces_in_bulk(file: UploadFile = File(..., description="A ZIP file containing multiple face images.")):

    file_name = os.getcwd()+"/faceImages.zip"
    with open(file_name,'wb+') as f:
        f.write(file.file.read())
        f.close()

    # connect to the db
    con = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password)

    # cursor
    cur = con.cursor()

    # Create a ZipFile Object and load sample.zip in it
    with ZipFile('faceImages.zip', 'r') as zipObj:
        # Get a list of all archived file names from the zip
        listOfFileNames = zipObj.namelist()
        # Iterate over the file names
        for fileName in listOfFileNames:
            zipObj.extract(fileName, 'Images')
            file_name = os.getcwd()+"/Images/"+fileName
            print(fileName)
            cur.execute(
                "insert into face_images(name,date,location,imageUrl) values('" + fileName + "','','','" + file_name + "')")

    # commit the transcation
    con.commit()

    # close the cursor
    cur.close()

    # close the connection
    con.close()

    return {"status": "OK", "body": "Images Successfully Added To The Database"}


@app.post("/get_face_info/")
async def get_face_info(face_id: str = Form(...)):

    # connect to the db
    con = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password)

    # cursor
    cur = con.cursor()

    # execute query
    cur.execute("select * from face_images where id = "+face_id)

    rows = cur.fetchall()
    temp = "{ "
    for r in rows:
        temp += f"id : {r[0]}, Name : {r[1]}, Date : {r[2]}, Location : {r[3]}"
    temp += " }"

    # close the cursor
    cur.close()

    # close the connection
    con.close()

    return {"status": "OK", "body": {"match": temp}}

