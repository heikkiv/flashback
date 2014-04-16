#!/usr/bin/python

import sys
sys.path.insert(0, 'lib')

import authenticator
import pprint
import httplib2
from apiclient.discovery import build
from datetime import date

def get_year_month_day():
  today = date.today()
  return (today.year, today.month, today.day)
  

def list_files(service, folder):
  id = folder['id']
  query = "'{}' in parents".format(id)
  files = service.files().list(q=query,maxResults=1000).execute()
  for file in files['items']:
    if file['mimeType'] == 'application/vnd.google-apps.folder':
      print '-' + file['title']
    else:
      print file['title']


def find_files(service, parent_folder, date_tuple):
  files = []
  year_folder = find_folder(service, parent_folder, str(date_tuple[0]))
  if year_folder:
    print "Found year: " + year_folder['title']
    month = "{0:02d}".format(date_tuple[1])
    month_folder = find_folder(service, year_folder, str(month))
    if month_folder:
      print "Found month: " + month_folder['title']
      day = "{0:02d}".format(date_tuple[2])
      day_folder = find_folder(service, month_folder, str(day))
      if day_folder:
        print "Found day: " + day_folder['title']
        files = find_files_in_folder(service, day_folder)['items']
        print "Found {} files".format(len(files))
  return files


def find_folder(service, parent_folder, name):
  id = parent_folder['id']
  query = "'{}' in parents".format(id)
  files = service.files().list(q=query,maxResults=1000).execute()
  for file in files['items']:
    if file['mimeType'] == 'application/vnd.google-apps.folder' and file['title'] == name:
      return file
  return None
  

def find_files_in_folder(service, parent_folder):
  id = parent_folder['id']
  query = "'{}' in parents".format(id)
  files = service.files().list(q=query,maxResults=1000).execute()
  return files


def main():
  credentials = authenticator.get_credentials()

  # Create an httplib2.Http object and authorize it with our credentials
  http = httplib2.Http()
  http = credentials.authorize(http)
    
  service = build('drive', 'v2', http=http)

  today = get_year_month_day()
  
  #file = drive_service.files().insert(body=body, media_body=media_body).execute()
  #files = drive_service.files().list(q="mimeType = 'application/vnd.google-apps.folder'",maxResults=10).execute()
  pictures_folder = service.files().get(fileId='0B1lcwvVRt_4zOEV1czhiZWN1NVE').execute()
  files = find_files(service, pictures_folder, (today[0] - 1, today[1], today[2]))
  for file in files:
    print file['title']
  #list_files(service, files['items'][0])
  #pprint.pprint(files)

if __name__ == "__main__":
    main()
