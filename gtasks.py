# vtasks, a terminal google tasks client, MIT license
# this file deals with the Google tasks API - creidt to the following blog post:
# http://parezcoydigo.wordpress.com/2011/05/16/google-tasks-terminal-geek-tool/
# which is what this code was initially based on

import time
import re
import datetime
import httplib2
import keyring
import sys
from os import path
from datetime import date

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run

# Set up a Flow object to be used if we need to authenticate. This
# requires having set up a Google app for yourself and downloading
# the client_secrets.json file into the same directory.
DIRECTORY = path.split(path.realpath(__file__))[0]
FLOW = flow_from_clientsecrets(path.join(DIRECTORY, 'client_secrets.json'), scope='https://www.googleapis.com/auth/tasks')

# If the Credentials don't exist or are invalid, run through the native client
# flow. The Storage object will ensure that if successful the good
# Credentials will get written back to a file.
storage = Storage(path.join(DIRECTORY, 'vtasks.dat'))
credentials = storage.get()
if credentials is None or credentials.invalid == True:
  credentials = run(FLOW, storage)

# Create an httplib2.Http object to handle our HTTP requests and authorize it
# with our good Credentials.
http = httplib2.Http()
http = credentials.authorize(http)

# Build a service object for interacting with the API. Visit
# the Google APIs Console
# to get a developerKey for your own application.
service = build(serviceName='tasks', version='v1', http=http,
       developerKey=keyring.get_password('googleDevKey', 'finlaysoni@gmail.com'))


# a class for storing a task
class Task:
  def __init__(self, task, tasklist):
    self.task = task
    self.tasklist = tasklist

  # return the text of this task
  def text(self):
    return self.task['title']

  # return the due date of this task
  def due(self):
    if 'due' in self.task:
      return str(self.task['due'])[5:-14]
    else:
      return ''

  # write this task to a file suitable for editing
  def write_file(self, fname):
    f = open(fname, 'w')
    # if there's a due date, write it on line one
    if 'due' in self.task:
      f.write(self.due( ))
      f.write('\n')
    # write the text of it onto the next line
    f.write(self.text( ))
    f.close( )

  # return whether or not the task is completed
  def completed(self):
    return self.task['status'] == 'completed'

  # delete the current task
  def delete(self):
    service.tasks( ).delete(tasklist = self.tasklist['id'], task = self.task['id']).execute( )

  # check off the current task
  def check(self):
    # make an action thing where we have the same data, but switched the status to the opposite
    action = self.task
    if self.completed( ):
      action['status'] = 'needsAction'
      del action['completed']
    else:
      action['status'] = 'completed'
      action['completed'] = datetime.datetime.utcnow( ).isoformat("T") + "Z"
    service.tasks( ).update(tasklist = self.tasklist['id'], task = self.task['id'], body = action).execute( )

# the following function returns a list of all tasks in the users list
def get_tasks( ):
  all_tasks = []
  # for each task list that they have
  tasklists = service.tasklists( ).list( ).execute( )
  for tasklist in tasklists['items']:
    listID = tasklist['id']
    # for each task in this list
    tasks = service.tasks( ).list(tasklist = listID).execute()
    for task in tasks['items']:
      # add an entry for this task
      all_tasks.append(Task(task, tasklist))
  # return all tasks
  return all_tasks

# add a task into the task list
def add_task(fname):
  # load the data from this file
  f = open(fname)
  data = f.readlines( )

  # condense the lines into one, and remove consecutive whitespace
  text = " ".join(data)
  text = " ".join(text.split( ))

  # find if there is a due date
  match = re.search('\d+-\d+(-\d+)*', text)
  if match:
    due = match.group( )
    # remove from original string
    text = text.replace(due + ' ', '')
    # if they didn't give a year, use the current
    # TODO it would be nicer if it looked at the month they gave
    # so if it's december, and they gave month 1-11, it should really use the *next*
    # year after the current one
    if due.count('-') < 2:
      due = str(date.today( ).year) + '-' + due
  else:
    due = None

  # TODO allow for different lists
  listName = 'Todo'

  # set up the task itself
  if due != None:
    task = {'title' : text, 'due' : due + 'T12:00:00.000Z'}
  else:
    task = {'title' : text}
  # find the task list by name
  tasklists = service.tasklists().list().execute()
  listID = None
  for tasklist in tasklists['items']:
    if listName == tasklist['title']:
      listID=tasklist['id']
      break
  # if not found make a new list (this won't happen)
  if listID == None:
    tasklist = {
      'title': listName,
      }
    result = service.tasklists().insert(body=tasklist).execute()
    listID = result['id']
  # actually insert the task
  newTask = service.tasks().insert(tasklist=listID, body=task).execute()


