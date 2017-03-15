import httplib2
from datetime import datetime

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run
import os



class FTable:
    def __init__(self, table_id, table_headings):
      '''table_id can be looked up in fusion tables: File | About This Table

      '''
      # CLIENT_SECRETS, name of a file containing the OAuth 2.0 information for this
      # application, including client_id and client_secret.
      # You can see the Client ID and Client secret on the API Access tab on the
      # Google APIs Console <https://code.google.com/apis/console>
      script_dir = os.path.dirname(os.path.realpath(__file__))
      CLIENT_SECRETS = script_dir + '/' + 'client_secrets.json'

      # Set up a Flow object to be used for authentication.
      # Add one or more of the following scopes. PLEASE ONLY ADD THE SCOPES YOU
      # NEED. For more information on using scopes please see
      # <https://developers.google.com/+/best-practices>.
      FLOW = flow_from_clientsecrets(CLIENT_SECRETS,
          scope=[
            'https://www.googleapis.com/auth/fusiontables',
            'https://www.googleapis.com/auth/fusiontables.readonly',
          ],
          message='missing client secrets')


      # If the Credentials don't exist or are invalid, run through the native
      # client flow. The Storage object will ensure that if successful the good
      # Credentials will get written back to a file.
      self.storage = Storage(script_dir + '/' + 'sample.dat')
      self.credentials = self.storage.get()
      self.table_id = table_id
      self.table_headings_str = ','.join(table_headings)

      if self.credentials is None or self.credentials.invalid:
        self.credentials = run(FLOW, self.storage)

      # Create an httplib2.Http object to handle our HTTP requests and authorize it
      # with our good Credentials.
      http = httplib2.Http()
      http = self.credentials.authorize(http)

      self.service = build('fusiontables', 'v1', http=http)  

    def rec(self, table_values):
      ''' table_values is a list of value strings
      '''
      sql_str = "INSERT INTO %s (%s) VALUES (%s)" % (self.table_id, self.table_headings_str, ', '.join(map(lambda x: "'" + x + "'", table_values)))
      print sql_str
      try:
        update_req = self.service.query().sql(sql=sql_str)
        update_req.execute()
    
      except AccessTokenRefreshError:
        print ("The credentials have been revoked or expired")

    def get(self):
      ''' returns a dictionary of parameters stored in table
      '''
      sql_str = "SELECT %s FROM %s" % (self.table_headings_str, self.table_id)
      print sql_str
      try:
        get_req = self.service.query().sql(sql=sql_str)
        resp = get_req.execute()
        return dict(resp['rows'])
    
      except AccessTokenRefreshError:
        print ("The credentials have been revoked or expired")


if __name__ == '__main__':
  #ft = FTable('1bUexdzlMGGkJQnPFgzuIYkn_Jw7g3c9lysc7oUM', ['seq', 'temp'])
  #tstamp = datetime.now().strftime('%m/%d/%y %I:%M %p')
  #ft.rec((tstamp, '77.7'))

  #ft = FTable('1KsdUMd1Bo-bt_1k2I7MnmdKKJHhRvD2LL4eKItc', ['Timestamp', 'Temperature', 'State', 'Message'])
  #tstamp = datetime.now().strftime('%m/%d/%y %I:%M %p')
  #ft.rec((tstamp, '77.7', 'HOT', 'some long message with number 55.4 included 55.4'))
  import pprint
  ft = FTable('1jjmCTe_RjbQE3OYXJ5yUEcIjYPCUbETzuWIJP6o', ['Parameter', 'Value'])
  params = ft.get();
  #for i in params:
  #  print i
  print params



