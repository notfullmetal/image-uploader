from fastapi import FastAPI, Request, UploadFile, HTTPException, status, Form
from fastapi.responses import HTMLResponse, JSONResponse
import aiofiles
import requests
import os
import pathlib

app = FastAPI()


async def upload_image_to_catbox(file_path: str) -> str:
    file_extension = pathlib.Path(file_path).suffix.lower()
    if file_extension in ['.jpeg', '.jpg']:
        mime_type = 'image/jpeg'
    elif file_extension == '.png':
        mime_type = 'image/png'
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Unsupported file type'
        )
    
    async with aiofiles.open(file_path, 'rb') as image_file:
        contents = await image_file.read()
        files = {'fileToUpload': ('filename', contents, mime_type)}
        data = {
            'reqtype': 'fileupload'
            }
        response = requests.post('https://catbox.moe/user/api.php', files=files, data=data)

        response_json = {
            'content': response.text,
            'status_code': response.status_code
        }

        return JSONResponse(content=response_json)
    
async def upload_image_to_graph(file_path: str) -> str:
    file_extension = pathlib.Path(file_path).suffix.lower()
    if file_extension in ['.jpeg', '.jpg']:
        mime_type = 'image/jpeg'
    elif file_extension == '.png':
        mime_type = 'image/png'
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Unsupported file type'
        )
    
    async with aiofiles.open(file_path, 'rb') as image_file:
        contents = await image_file.read()
        files = {'file': ('filename', contents, mime_type)}
        data = {}
        response = requests.post('https://graph.org/upload', data=data, files=files)

        response_json = {
            'content': response.text
        }

        return JSONResponse(content=response_json)


@app.post('/upload')
async def upload(file: UploadFile, destination: str = Form(...)):
    try:
        async with aiofiles.open(file.filename, 'wb') as f:
            contents = await file.read()
            await f.write(contents)

        if destination =='catbox':
            url = await upload_image_to_catbox(file.filename)
        elif destination =='graph':
            url = await upload_image_to_graph(file.filename)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Invalid upload destination'
            )

        if os.path.exists(file.filename):
            os.remove(file.filename)

        return {'message': 'File uploaded successfully', 'url': url}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'There was an error: {str(e)}'
        )
    finally:
        await file.close()

    
# @app.get('/')
# async def main():
#     content = '''
#     <body>
#     <form action='/upload' enctype='multipart/form-data' method='post'>
#     <input name='file' type='file'>
#     <input type='submit'>
#     </form>
#     </body>
#     '''
#     return HTMLResponse(content=content)

@app.get('/')
async def main():
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
            <form action='/upload' enctype='multipart/form-data' method='post'>
                <input name='file' type='file' required>
                <div>
                    <button type='submit' name='destination' value='catbox'>Upload to Catbox</button>
                    <button type='submit' name='destination' value='graph'>Upload to Graph</button>
                </div>
            </form>
        </div>
    </body>
    </html>
    '''
    return HTMLResponse(content=content)