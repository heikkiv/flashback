#!/usr/bin/python
# coding=utf-8

import sys

sys.path.insert(0, 'lib')

import authenticator
import mailer
import downloader

import httplib2
from apiclient.discovery import build
from datetime import date
from random import randint
import ConfigParser


def get_year_month_day():
    today = date.today()
    return today.year, today.month, today.day


def list_files(service, folder):
    id = folder['id']
    query = "'{}' in parents".format(id)
    files = service.files().list(q=query, maxResults=1000).execute()
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
    files = service.files().list(q=query, maxResults=1000).execute()
    for file in files['items']:
        if file['mimeType'] == 'application/vnd.google-apps.folder' and file['title'] == name:
            return file
    return None


def find_files_in_folder(service, parent_folder):
    id = parent_folder['id']
    query = "'{}' in parents".format(id)
    files = service.files().list(q=query, maxResults=1000).execute()
    return files


def main(source, recipients):
    config = ConfigParser.ConfigParser()
    config.readfp(open('config.cfg'))
    aws_credentials = (config.get('default', 'aws_access_key_id'), config.get('default', 'aws_access_key_secret'))

    google_credentials = authenticator.get_credentials()

    # Create an httplib2.Http object and authorize it with our google_credentials
    http = httplib2.Http()
    http = google_credentials.authorize(http)

    service = build('drive', 'v2', http=http)

    today = get_year_month_day()
    print "Today is %d.%d.%d" % (today[2], today[1], today[0])

    pictures_folder_file_id = '0B1lcwvVRt_4zOEV1czhiZWN1NVE'
    pictures_folder = service.files().get(fileId=pictures_folder_file_id).execute()

    selected_files = []
    for i in range(1, 10):
        target_day = (today[0] - i, today[1], today[2])
        print "Looking for photos taken on %d.%d.%d" % (target_day[2], target_day[1], target_day[0])

        files = find_files(service, pictures_folder, target_day)
        #for file in files:
        #print file['title']

        if files:
            i = randint(0, len(files) - 1)
            selected_files.append((target_day, files[i]))
            print "Selected: " + files[i]['title']

    if len(selected_files) > 0:
        print "Selected %d images in total" % len(selected_files)
        for date, drive_file in selected_files:
            print "Downloading " + drive_file['title']
            content = downloader.download_file(service, drive_file)
            f = open("/tmp/" + drive_file['title'], 'w')
            f.write(content)

        #filenames = [(day, unicode("/tmp/" + f['title'], "utf-8")) for (day, f) in selected_files]
        filenames = [(day, "/tmp/" + f['title']) for (day, f) in selected_files]

        mailer.send_email(today, source, recipients, filenames, aws_credentials)
        print "Mail sent with %d images" % len(selected_files)
    else:
        print "No images for today"

if __name__ == "__main__":
    source = sys.argv[1]
    recipients = sys.argv[2:]
    main(source, recipients)
