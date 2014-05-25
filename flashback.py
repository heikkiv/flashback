#!/usr/bin/python
# coding=utf-8

import sys

sys.path.insert(0, 'lib')

import authenticator
import mailer

import httplib2
from apiclient.discovery import build
from datetime import date
import random
import string
from apiclient import errors
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


def get_file(service, file_id):
    try:
        return service.files().get(fileId=file_id).execute()
    except errors.HttpError, error:
        print 'An error occurred: %s' % error
    return None


def copy_to_public_folder(service, origin_file_id, public_folder_id):
    title = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(32)) + '.jpg'
    copied_file = {'title': title}
    try:
        copied_file = service.files().copy(fileId=origin_file_id, body=copied_file).execute()
        original_parent = copied_file['parents'][0]['id']
        insert_file_into_folder(service, public_folder_id, copied_file['id'])
        remove_file_from_folder(service, original_parent, copied_file['id'])
        make_file_public(service, copied_file['id'])
        return copied_file
    except errors.HttpError, error:
        print 'An error occurred: %s' % error
    return None


def make_file_public(service, file_id):
    permission = {
        'value': '',
        'type': 'anyone',
        'role': 'reader'
    }
    return service.permissions().insert(fileId=file_id, body=permission).execute()


def insert_file_into_folder(service, folder_id, file_id):
    new_parent = {'id': folder_id}
    return service.parents().insert(fileId=file_id, body=new_parent).execute()


def remove_file_from_folder(service, folder_id, file_id):
    service.parents().delete(fileId=file_id, parentId=folder_id).execute()


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

    pictures_folder_file_id = config.get('default', 'pictures_folder_id')
    pictures_folder = get_file(service, pictures_folder_file_id)
    public_folder_id = config.get('default', 'public_folder_id')
    public_folder = get_file(service, public_folder_id)

    yearly_selected_files = []
    for i in range(1, 10):
        target_day = (today[0] - i, today[1], today[2])
        print "Looking for photos taken on %d.%d.%d" % (target_day[2], target_day[1], target_day[0])
        files = find_files(service, pictures_folder, target_day)
        if files:
            i = random.randint(0, len(files) - 1)
            yearly_selected_files.append((target_day, files[i]))

    if len(yearly_selected_files) > 0:
        i = random.randint(0, len(yearly_selected_files) - 1)
        selected_date = yearly_selected_files[i][0]
        selected_file = yearly_selected_files[i][1]
        print "Selected image %s from %d.%d.%d" % (selected_file['title'], selected_date[2], selected_date[1], selected_date[0])
        public_selected_file = copy_to_public_folder(service, selected_file['id'], public_folder_id)
        print "Copied selected image to public folder, id: %s" % public_selected_file['id']
        url = public_folder['webViewLink'] + public_selected_file['title']
        print url
        mailer.send_email(today, source, recipients, [(selected_date, url)], aws_credentials)
        print "Mail sent"
    else:
        print "No images for today"


if __name__ == "__main__":
    source = sys.argv[1]
    recipients = sys.argv[2:]
    main(source, recipients)
