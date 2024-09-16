from fastapi import FastAPI, Request, UploadFile, HTTPException, status, Form
from fastapi.responses import HTMLResponse, JSONResponse
import aiofiles
import requests
import os
import pathlib
import json
from dotenv import load_dotenv

app = FastAPI()

load_dotenv()

def upload_image_to_catbox(file_content: bytes, filename: str) -> str:
    # file_extension = pathlib.Path(filename).suffix.lower()
    # if file_extension in ['.jpeg', '.jpg']:
    #     mime_type = 'image/jpeg'
    # elif file_extension == '.png':
    #     mime_type = 'image/png'
    # else:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail='Unsupported file type'
    #     )
    
    # with open(filename, 'rb') as image_file:
    #     contents = await image_file.read()
    #     files = {'fileToUpload': (image_file, file_content)}
    #     data = {
    #         'reqtype': 'fileupload'
    #         }

    files = {'fileToUpload': (filename, file_content)}
    data = {
        'reqtype': 'fileupload'
    }
    response = requests.post('https://catbox.moe/user/api.php', files=files, data=data)

    # response_json = {
    #     'content': response.text
    # }
    # response_filter= json.dumps(response_json)

    # return (response_filter)

    #return JSONResponse(content=response_json)

    return response.text.strip()
    
# def upload_image_to_graph(file_content: bytes, filename: str) -> str:
#     file_extension = pathlib.Path(filename).suffix.lower()
#     if file_extension in ['.jpeg', '.jpg']:
#         mime_type = 'image/jpeg'
#     elif file_extension == '.png':
#         mime_type = 'image/png'
#     else:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail='Unsupported file type'
#         )
    
#     # async with aiofiles.open(file_path, 'rb') as image_file:
#     #     contents = await image_file.read()
#     #     files = {'file': ('filename', contents, mime_type)}
#     #     data = {}

#     files = {'file': (filename, file_content, mime_type)}
#     response = requests.post('https://graph.org/upload', files=files)

#     # response_json = {
#     #     'content': response.text
#     # }

#     #return JSONResponse(content=response_json)

#     response_json = response.json()
#     file_path = "https://graph.org" + response_json[0]['src']

#     return file_path

def upload_image_to_imgur(file_content: bytes, filename: str, client_id: str) -> str:
    client_id = '546c25a59c58ad7'
    url = 'https://api.imgur.com/3/image'
    headers = {
        'Authorization': f'Client-ID {client_id}'
    }
    files = {'image': file_content}
    response = requests.post(url, headers=headers, files=files)

    # Check if the request was successful
    if response.status_code == 200:
        # Get the link to the uploaded image
        return response.json()['data']['link']
    else:
        raise Exception(f"Failed to upload image: {response.status_code} {response.text}")

@app.post('/upload')
def upload(file: UploadFile, destination: str = Form(...)):
    try:
        # with open(file.filename, 'wb') as f:
        #     contents = file.read()
        #     f.write(contents)

        imgur_client_id = os.getenv('IMGUR_CLIENT_ID')

        file_content = file.file.read()

        if destination =='catbox':
            url = upload_image_to_catbox(file_content, file.filename)
        elif destination =='imgur':
            if not imgur_client_id:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail='Imgur client ID is missing'
                )
            url = upload_image_to_imgur(file_content, file.filename, imgur_client_id)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Invalid upload destination'
            )

        if os.path.exists(file.filename):
            os.remove(file.filename)

        return {'status': 'Success', 'url': url}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'There was an error: {str(e)}'
        )
    finally:
        file.file.close()

@app.get('/')
def main():
    content = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Upload File</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .upload-container {
                background-color: #fff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                text-align: center;
            }
            .upload-container h1 {
                margin-bottom: 20px;
                color: #333;
            }
            .upload-container input[type="file"] {
                margin-bottom: 20px;
            }
            .upload-container button {
                background-color: #007bff;
                color: #fff;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                cursor: pointer;
                margin: 5px;
            }
            .upload-container button:hover {
                background-color: #0056b3;
            }
        </style>
    </head>
    <body>
    <div class="upload-container">
    <h1>Upload Your File</h1>
    <form id="uploadForm" action='/upload' enctype='multipart/form-data' method='post'>
        <input id="fileInput" name='file' type='file' required>
        
        <div class="dropdown">
            <button class="dropbtn" style="pointer-events: none; cursor: default;">Upload</button>

            <div class="dropdown-content">
                <button type="button" name="destination" value="catbox" onclick="submitForm('catbox')">Upload to Catbox</button>
                <button type="button" name="destination" value="imgur" onclick="submitForm('imgur')">Upload to Imgur</button>
            </div>
        </div>

        <div class="error" id="errorMessage"></div>
    </form>
    <div id="uploadedUrl"></div>
    </div>

    <style>
        .upload-container {
            text-align: center;
            margin-top: 50px;
        }

        .dropdown {
            position: relative;
            display: inline-block;
        }

        .dropbtn {
            background-color: #007bff;
            color: white;
            padding: 10px 20px;
            font-size: 16px;
            border: none;
            cursor: pointer;
            border-radius: 4px;
        }

        .dropdown-content {
            display: none;
            position: absolute;
            background-color: #f9f9f9;
            min-width: 160px;
            box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
            z-index: 1;
        }

        .dropdown-content button {
            background-color: white;
            color: black;
            padding: 12px 16px;
            border: none;
            width: 100%;
            text-align: left;
            cursor: pointer;
        }

        .dropdown-content button:hover {
            background-color: #f1f1f1;
        }

        .dropdown:hover .dropdown-content {
            display: block;
        }

        .dropdown:hover .dropbtn {
            background-color: #0056b3;
        }
    </style>

    <script>
    function submitForm(destination) {
        var fileInput = document.getElementById('fileInput');
        var errorMessage = document.getElementById('errorMessage');
        var uploadedUrl = document.getElementById('uploadedUrl');
        var maxSize = 4 * 1024 * 1024;

        if (fileInput.files.length > 0) {
            var file = fileInput.files[0];
            if (file.size > maxSize) {
                errorMessage.textContent = 'File size exceeds 4MB limit.';
                return;
            }

            errorMessage.textContent = '';

            var formData = new FormData();
            formData.append("file", file);
            formData.append("destination", destination);

            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === "Success") {
                    uploadedUrl.innerHTML = '<p>Uploaded successfully! URL: <a href="' + data.url + '" target="_blank">' + data.url + '</a></p>';
                } else {
                    uploadedUrl.innerHTML = '<p>Error: ' + data.detail + '</p>';
                }
            })
            .catch(error => {
                uploadedUrl.innerHTML = '<p>Error: ' + error + '</p>';
            });
        } else {
            errorMessage.textContent = 'Please select a file to upload.';
        }
    }
    </script>
    
</body>
</html>
    '''
    return HTMLResponse(content=content)