import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote
from google.appengine.ext import ndb
from google.appengine.ext.ndb import msgprop



# TODO: Replace the following lines with client IDs obtained from the APIs
# Console or Cloud Console.
WEB_CLIENT_ID = '588516474194-nvessqc4mhp2rvufhpkm9oc53bhsfl9n.apps.googleusercontent.com'
ANDROID_CLIENT_ID = 'replace this with your Android client ID'
IOS_CLIENT_ID = 'replace this with your iOS client ID'
ANDROID_AUDIENCE = WEB_CLIENT_ID

package = 'Conference'

class TeeShirtSize(messages.Enum):
  NOT_SPECIFIED, XS, S, M, L, XL, XXL, XXXL = range(8)
  # def __init__(self, displayName, teeShirtSize):
  #   self.displayName = displayName
  #   self.teeShirtSize = teeShirtSize
  # def getDisplayName(self):
  #   return self.displayName
  # def getTeeShirtSize(self):
  #   return self.teeShirtSize

class Profile(messages.Message):
  # def __init__(self, userId, displayName, mainEmail, teeShirtSize):
  #   self.userId = userId
  #   self.displayName = displayName
  #   self.mainEmail = mainEmail
  #   self.teeShirtSize = teeShirtSize
  # def getDisplayName(self):
  #   return self.displayName
  # def getMainEmail(self):
  #   return self.mainEmail
  # def getTeeShirtSize(self):
  #   return self.teeShirtSize
  # def getUserId(self):
  #   return self.userId
  userId = messages.IntegerField(1)
  displayName = messages.StringField(2)
  mainEmail = messages.StringField(3)
  teeShirtSize = messages.EnumField(TeeShirtSize, 4)

class ProfileStore(ndb.Model):
  created_time = ndb.DateTimeProperty(auto_now_add=True)
  profile = msgprop.MessageProperty(Profile, indexed_fields=["mainEmail", "displayName", "teeShirtSize"])

@endpoints.api(name='conference', version='v1',
               allowed_client_ids=[WEB_CLIENT_ID, ANDROID_CLIENT_ID,
                                   IOS_CLIENT_ID])
class ConferenceApi(remote.Service):
    """Conference API v1."""

    PROFILE_RESOURCE = endpoints.ResourceContainer(
      message_types.VoidMessage,
      displayName=messages.StringField(2),
      teeShirtSize=messages.EnumField(TeeShirtSize, 4))

    @endpoints.method(PROFILE_RESOURCE, Profile,
                      path='profile/{displayName, teeShirtSize}', http_method='POST',
                      name='saveProfile')
    def saveProfile(self, request):
      try:
        user = endpoints.get_current_user()
      except():
        raise endpoints.UnauthorizedException("Authorization required")
      userId = user.user_id()
      mainEmail = user.email()
      displayName = request.displayName if request.displayName else "Your name will go here"
      teeShirtSize = request.teeShirtSize if request.teeShirtSize else TeeShirtSize.NOT_SPECIFIED

      profile = Profile(userId=userId, mainEmail=mainEmail, displayName=displayName, teeShirtSize=teeShirtSize)
      p = ProfileStore.get_or_insert(mainEmail)
      p.profile = profile
      p.put()
      return profile

    @endpoints.method(message_types.VoidMessage, Profile,
                      path='profile', http_method='GET',
                      name='getProfile')
    def getProfile(self, request):
      try:
        user = endpoints.get_current_user()
      except():
        raise endpoints.UnauthorizedException("Authorization required")
      P = ProfileStore.get_by_id(user.email())
      if P:
        return P.profile
      else:
        userId = user.user_id()
        mainEmail = user.email()
        displayName = mainEmail.split("@")[0] if mainEmail else "Your name will go here"
        teeShirtSize = TeeShirtSize.NOT_SPECIFIED
        return Profile(userId=userId, mainEmail=mainEmail, displayName=displayName, teeShirtSize=teeShirtSize)

APPLICATION = endpoints.api_server([ConferenceApi])