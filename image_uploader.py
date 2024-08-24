from fastapi import FastAPI, Request, UploadFile, HTTPException, status
from fastapi.responses import HTMLResponse
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
        files = {'fileToUpload': ('file', contents, mime_type)}
        data = {
            'reqtype': 'fileupload'
            }
        response = requests.post('https://catbox.moe/user/api.php', files=files, data=data)

    if response.status_code == 200:
        base_url = response.text.strip()
        return base_url
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to upload the image to Catbox.moe'
        )
    

@app.post('/upload')
async def upload(file: UploadFile):
    try:
        async with aiofiles.open(file.filename, 'wb') as f:
            contents = await file.read()
            await f.write(contents)

        catbox_url = await upload_image_to_catbox(file.filename)

        if os.path.exists(file.filename):
            os.remove(file.filename)

        return {'message': 'File uploaded successfully', 'catbox_url': catbox_url}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'There was an error: {str(e)}'
        )
    finally:
        await file.close()

    
@app.get('/')
async def main():
    content = '''
    <body>
    <form action='/upload' enctype='multipart/form-data' method='post'>
    <input name='file' type='file'>
    <input type='submit'>
    </form>
    </body>
    '''
    return HTMLResponse(content=content)