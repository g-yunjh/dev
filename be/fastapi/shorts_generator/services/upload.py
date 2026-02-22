import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

def authenticate_with_drive(credentials_json, token_file="token.json"):
    """
    Authenticates with Google Drive API using token.json if available.

    :param credentials_json: Path to the credentials.json file
    :param token_file: Path to save the authentication token
    :return: Google Drive service object
    """
    try:
        creds = None
        # Check if token file exists
        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, ['https://www.googleapis.com/auth/drive.file'])
        else:
            # Authenticate using credentials.json and save token
            flow = InstalledAppFlow.from_client_secrets_file(credentials_json, ['https://www.googleapis.com/auth/drive.file'])
            creds = flow.run_local_server(port=0)
            with open(token_file, "w") as token:
                token.write(creds.to_json())
            print("Authentication successful, token saved.")

        # Build and return the Drive service object
        return build('drive', 'v3', credentials=creds)
    except Exception as e:
        print(f"Error during authentication: {e}")
        return None

def upload_to_google_drive(service, file_path, file_name):
    """
    Uploads a file to Google Drive using saved credentials.

    :param file_path: Path to the local file
    :param file_name: Name of the file on Google Drive
    :param token_file: Path to the authentication token
    """
    try:
        # Create a media upload object
        media = MediaFileUpload(file_path, resumable=True)

        # Upload the file
        file_metadata = {
            'name': file_name,
            'parents': ['1PtJFOMkW-ikjdzBVIKO5fqwReq91Mau8']
            }
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

        print(f"File uploaded successfully. File ID: {file.get('id')}")
        return file.get('id')
    except Exception as e:
        print(f"Error uploading to Google Drive: {e}")
        return None