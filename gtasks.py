# this file deals with the Google tasks API - creidt to the following blog post:
# http://parezcoydigo.wordpress.com/2011/05/16/google-tasks-terminal-geek-tool/
# which is what this code was initially based on

import datetime
import httplib2
import keyring
import sys

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run

# Set up a Flow object to be used if we need to authenticate. This
# requires having set up a Google app for yourself and downloading
# the client_secrets.json file into the same directory.
FLOW = flow_from_clientsecrets('client_secrets.json', scope='https://www.googleapis.com/auth/tasks')

# If the Credentials don't exist or are invalid, run through the native client
# flow. The Storage object will ensure that if successful the good
# Credentials will get written back to a file.
storage = Storage('vtasks.dat')
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
      action['status'] = 'needsAction'  # FIXME why does this fail?
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










def main(*argv):
# To add a task, the command is 'n'. Then, pass three arguments-- listName, newTask, dueDate.
# ex: tasks n listName "This is my task." 2011-01-01
  if sys.argv[1] == 'n':
    listName = sys.argv[2]
    task = {
      'title': sys.argv[3], 
      'due': sys.argv[4]+'T12:00:00.000Z',
      }         
    tasklists = service.tasklists().list().execute()
    listID = None
    for tasklist in tasklists['items']:
      if listName == tasklist['title']:
        listID=tasklist['id']
        break
    if listID == None:
      tasklist = {
        'title': listName,
        }
      result = service.tasklists().insert(body=tasklist).execute()
      listID = result['id']       
    newTask = service.tasks().insert(tasklist=listID, body=task).execute()

# clear completed tasks from all lists
# tasks c
  if sys.argv[1] == 'c':
    tasklists = service.tasklists().list().execute()
    for tasklist in tasklists['items']:
      listID = tasklist['id']
      
      service.tasks().clear(tasklist=listID, body='').execute()


if __name__ == '__main__':
  main()  

