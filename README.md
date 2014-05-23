# vtasks

A terminal google tasks client.

### Dependencies
Below are the dependencies needed for vtasks, along with instructions
on how to fulfill them:

- A google account (obviously).
- Python version 2.  This is installed on most Linux systems.
- python-httplib2.  This can be installed on ubuntu by "sudo aptitude install
python-httplib2".
- python-keyring.  This can be installed on ubuntu by "sudo aptitude install
python-keyring".
- python-gflags.  This can be installed with "sudo aptitude installed python-gflags".
- The Google Python API's.  This can be installed with the "easy\_install"
Python program: "sudo easy\_install --upgrade google-api-python-client".


### Setting up a Developers Key
To use vtasks, you need to set up a Google developer key.  This is a key you
register with Google that lets you call their APIs.  It's not very convenient
that everyone needs their own, but it seems the APIs are much more geared
towards web development, where many people use the same application.

You can attain a developer key by:
1. Navigate to https://console.developers.google.com/project and clicking "Create Project".
2.  Enter a name and submit.
3. Click on the "APIs" link on the left, and turn on the "Tasks API".
4. Next click on the "Credentials" link on the left.
5. Click Create new client ID.
6. Choose "Installed Application", and "Other", then click Create.
7. Under the new Client ID for native application, click "Download JSON".  This
   will download a file called "client\_secret[stuff].json".
8. Rename this file to just "client\_secrets.json" and place it in the vtasks
   directory.

### Execution
Finally, you should be able to execute "python2 vtasks.py".  This will open a
web browser, prompting you to sign into Google if you have not already, and
confirm that vtasks can access your tasks data.  What happens next depends
slightly on your setup.  Either you will be given a code to paste into vtasks,
or a password manager will ask you to enter your user password.  Either way,
this is a one time step.  From then on vtasks should open on startup, with
no hassle.

### Usage




