import gflags
import httplib2
import keyring
import sys

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run

FLAGS = gflags.FLAGS

# Set up a Flow object to be used if we need to authenticate. This
# sample uses OAuth 2.0, and we set up the OAuth2WebServerFlow with
# the information it needs to authenticate. Note that it is called
# the Web Server Flow, but it can also handle the flow for native
# applications
# The client_id and client_secret are copied from the API Access tab on
# the Google APIs Console
FLOW = flow_from_clientsecrets('client_secrets.json',
    scope='https://www.googleapis.com/auth/tasks')

# To disable the local server feature, uncomment the following line:
FLAGS.auth_local_webserver = False

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


def main(*argv):
 
# Display all tasks in all lists. 
# ex.: tasks ls

  if sys.argv[1] == 'ls':
    tasklists = service.tasklists().list().execute()
    for tasklist in tasklists['items']:
      print tasklist['title']
      listID=tasklist['id']
      tasks = service.tasks().list(tasklist=listID).execute()
      for task in tasks['items']:
        dueDate=''
        if 'due' in task: 
          fullDueDate=str(task['due'])
          dueDate=fullDueDate[:10] 
        print '    '+task['title']+' : '+dueDate
      print


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

