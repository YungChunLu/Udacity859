import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote
from google.appengine.ext import ndb
from google.appengine.ext.ndb import msgprop



# TODO: Replace the following lines with client IDs obtained from the APIs
# Console or Cloud Console.
#WEB_CLIENT_ID = '588516474194-ick0d5d3788sf2tqj1hpfuq2bn4pa65r.apps.googleusercontent.com'
#For localhost
WEB_CLIENT_ID = '588516474194-nvessqc4mhp2rvufhpkm9oc53bhsfl9n.apps.googleusercontent.com'
ANDROID_CLIENT_ID = 'replace this with your Android client ID'
IOS_CLIENT_ID = 'replace this with your iOS client ID'
ANDROID_AUDIENCE = WEB_CLIENT_ID

package = 'Conference'

class TeeShirtSize(messages.Enum):
  NOT_SPECIFIED, XS, S, M, L, XL, XXL, XXXL = range(8)

class Profile(messages.Message):
  userId = messages.StringField(1)
  displayName = messages.StringField(2)
  mainEmail = messages.StringField(3)
  teeShirtSize = messages.EnumField(TeeShirtSize, 4)

class ProfileStore(ndb.Model):
  created_time = ndb.DateTimeProperty(auto_now_add=True)
  profile = msgprop.MessageProperty(Profile, indexed_fields=["userId",
                                                             "mainEmail",
                                                             "displayName",
                                                             "teeShirtSize"])

class Conference(messages.Message):
  name = messages.StringField(1)
  description = messages.StringField(2)
  topics = messages.StringField(3, repeated=True)
  city = messages.StringField(4)
  startDate = message_types.DateTimeField(5)
  endDate = message_types.DateTimeField(6)
  maxAttendees = messages.IntegerField(7)
  organizerDisplayName = messages.StringField(8)
  websafeKey = messages.IntegerField(9)

class ConferenceCollection(messages.Message):
  conferences = messages.MessageField(Conference, 1, repeated=True)

class ConferenceStore(ndb.Model):
  created_time = ndb.DateTimeProperty(auto_now_add=True)
  month = ndb.IntegerProperty()
  seatsAvailable = ndb.IntegerProperty()
  creator = ndb.StructuredProperty(ProfileStore)
  conference = msgprop.MessageProperty(Conference, indexed_fields=["topics",
                                                                   "name",
                                                                   "city",
                                                                   "organizerDisplayName"])

class Field(messages.Enum):
  CITY, TOPIC, MONTH, MAX_ATTENDEES = range(4)

class Operator(messages.Enum):
  EQ, LT, GT, LTEQ, GTEQ, NE = range(6)

class Filter(messages.Message):
  field = messages.EnumField(Field, 1)
  operator = messages.EnumField(Operator, 2)
  value = messages.StringField(3)

class Filters(messages.Message):
  filters = messages.MessageField(Filter, 1, repeated=True)

@endpoints.api(name='conference', version='v1',
               allowed_client_ids=[WEB_CLIENT_ID, ANDROID_CLIENT_ID,
                                   IOS_CLIENT_ID])
class ConferenceApi(remote.Service):
    """Conference API v1."""

    # Those query generating functions of filters
    def CITY(self, filter):
      if filter.operator == Operator.EQ:
        return (True, "ConferenceStore.conference.city == '%s'" % filter.value)
      else:
        return (False, "")
    def TOPIC(self, filter):
      if filter.operator == Operator.EQ:
        return (True, "ConferenceStore.conference.topics == '%s'" % filter.value)
      elif filter.operator == Operator.NE:
        return (True, "ConferenceStore.conference.topics != '%s'" % filter.value)
      else:
        return (False, "")
    def MONTH(self, filter):
      if filter.operator == Operator.EQ:
        return (True, "ConferenceStore.month == %s" % filter.value)
      elif filter.operator == Operator.LT:
        return (True, "ConferenceStore.month < %s" % filter.value)
      elif filter.operator == Operator.GT:
        return (True, "ConferenceStore.month > %s" % filter.value)
      elif filter.operator == Operator.LTEQ:
        return (True, "ConferenceStore.month <= %s" % filter.value)
      elif filter.operator == Operator.GTEQ:
        return (True, "ConferenceStore.month >= %s" % filter.value)
      elif filter.operator == Operator.NE:
        return (True, "ConferenceStore.month != %s" % filter.value)
      else:
        return (False, "")
    def MAX_ATTENDEES(self, filter):
      if filter.operator == Operator.EQ:
        return (True, "ConferenceStore.conference.maxAttendees == %s" % filter.value)
      elif filter.operator == Operator.LT:
        return (True, "ConferenceStore.conference.maxAttendees < %s" % filter.value)
      elif filter.operator == Operator.GT:
        return (True, "ConferenceStore.conference.maxAttendees > %s" % filter.value)
      elif filter.operator == Operator.LTEQ:
        return (True, "ConferenceStore.conference.maxAttendees <= %s" % filter.value)
      elif filter.operator == Operator.GTEQ:
        return (True, "ConferenceStore.conference.maxAttendees >= %s" % filter.value)
      elif filter.operator == Operator.NE:
        return (True, "ConferenceStore.conference.maxAttendees != %s" % filter.value)
      else:
        return (False, "")
    def checkFilter(self, filter):
      return {Field.CITY: self.CITY,
              Field.TOPIC: self.TOPIC,
              Field.MONTH: self.MONTH,
              Field.MAX_ATTENDEES: self.MAX_ATTENDEES}[filter.field](filter)

    @endpoints.method(Filters, ConferenceCollection,
                      path='queryConferences',
                      http_method='POST',
                      name='queryConferences')
    def queryConferences(self, request):
      user = endpoints.get_current_user()
      if user:
        queries = [q[1] for q in map(self.checkFilter, request.filters) if q[0]]
        if queries:
          query = "ndb.AND(%s)" % ','.join(queries)
          conferences = [ c.conference for c in ConferenceStore.query(eval(query)).fetch()]
        else:
          conferences = [ c.conference for c in ConferenceStore.query().order(ConferenceStore.month).fetch()]
        return ConferenceCollection(conferences=conferences)
      else:
        raise endpoints.UnauthorizedException("Authorization required")

    @endpoints.method(message_types.VoidMessage, ConferenceCollection,
                      path='getConferencesCreated',
                      http_method='POST',
                      name='getConferencesCreated')
    def getConferencesCreated(self, request):
      user = endpoints.get_current_user()
      if user:
        profile = ProfileStore.get_by_id(user.email())
        print profile
        conferences = [ c.conference for c in ConferenceStore.query(ConferenceStore.creator.profile.mainEmail==profile.profile.mainEmail).order(ConferenceStore.conference.name).fetch()]
        return ConferenceCollection(conferences=conferences)
      else:
        raise endpoints.UnauthorizedException("Authorization required")

    Detail_RESOURCE = endpoints.ResourceContainer(
            message_types.VoidMessage,
            websafeKey=messages.IntegerField(1))
    @endpoints.method(Detail_RESOURCE, Conference,
                      path='getConference/{websafeKey}',
                      http_method='POST',
                      name='getConference')
    def getConference(self, request):
      user = endpoints.get_current_user()
      if user:
        key = ndb.Key(ConferenceStore, request.websafeKey)
        conferenceStore = key.get()
        print conferenceStore
        return conferenceStore.conference
      else:
        raise endpoints.UnauthorizedException("Authorization required")

    @endpoints.method(Conference, Conference,
                      path='conference/{name, description, topics, city, startDate, endDate, maxAttendees',
                      http_method='POST',
                      name='createConference')
    def createConference(self, request):
      user = endpoints.get_current_user()
      if user:
        profile = ProfileStore.get_by_id(user.email())
        if not profile:
          mainEmail = user.email()
          p = Profile(userId=user.user_id(),
                            mainEmail=mainEmail,
                            displayName=mainEmail.split("@")[0],
                            teeShirtSize=TeeShirtSize.NOT_SPECIFIED)
          profile = ProfileStore.get_or_insert(mainEmail)
          profile.profile = p
          profile.put()
        name = request.name
        description = request.description
        topics = request.topics
        city = request.city
        startDate = request.startDate
        endDate = request.endDate
        maxAttendees = request.maxAttendees

        conference = Conference(name=name,
                                description=description,
                                topics=topics,
                                city=city,
                                startDate=startDate,
                                endDate=endDate,
                                maxAttendees=maxAttendees,
                                organizerDisplayName=profile.profile.displayName,
                                websafeKey=None)
        month = startDate.month
        seatsAvailable = maxAttendees
        c = ConferenceStore(creator=profile, month=month, seatsAvailable=seatsAvailable, conference=conference)
        c.put()
        print c.key
        conference.websafeKey = c.key.id()
        c.conference = conference
        c.put()
        return conference
      else:
        raise endpoints.UnauthorizedException("Authorization required")

    @endpoints.method(Profile, Profile,
                      path='profile/{displayName, teeShirtSize}',
                      http_method='POST',
                      name='saveProfile')
    def saveProfile(self, request):
      user = endpoints.get_current_user()
      if user:
        userId = user.user_id()
        mainEmail = user.email()
        displayName = request.displayName
        teeShirtSize = request.teeShirtSize

        profile = Profile(userId=userId, mainEmail=mainEmail, displayName=displayName, teeShirtSize=teeShirtSize)
        p = ProfileStore.get_or_insert(mainEmail)
        p.profile = profile
        p.put()
        for c in ConferenceStore.query(ancestor=p.key).order(ConferenceStore.conference.name).fetch():
          c.conference.organizerDisplayName = displayName
          c.put()
        return profile
      else:
        raise endpoints.UnauthorizedException("Authorization required")

    @endpoints.method(message_types.VoidMessage, Profile,
                      path='profile', http_method='GET',
                      name='getProfile')
    def getProfile(self, request):
      user = endpoints.get_current_user()
      if user:
        P = ProfileStore.get_by_id(user.email())
        if P:
          return P.profile
        else:
          userId = user.user_id()
          mainEmail = user.email()
          displayName = mainEmail.split("@")[0] if mainEmail else "Your name will go here"
          teeShirtSize = TeeShirtSize.NOT_SPECIFIED
          return Profile(userId=userId, mainEmail=mainEmail, displayName=displayName, teeShirtSize=teeShirtSize)
      else:
        raise endpoints.UnauthorizedException("Authorization required")

APPLICATION = endpoints.api_server([ConferenceApi])