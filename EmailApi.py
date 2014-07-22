# import endpoints
# from protorpc import messages
# from protorpc import message_types
# from protorpc import remote
import webapp2
from google.appengine.api import mail
# class Conference(messages.Message):
#   name = messages.StringField(1)
#   description = messages.StringField(2)
#   topics = messages.StringField(3, repeated=True)
#   city = messages.StringField(4)
#   startDate = message_types.DateTimeField(5)
#   endDate = message_types.DateTimeField(6)
#   maxAttendees = messages.IntegerField(7)
#   organizerDisplayName = messages.StringField(8)
#   websafeKey = messages.IntegerField(9)

# @endpoints.api(name='sendEmail', version='v1',
#                allowed_client_ids=[])
class EmailApi(webapp2.RequestHandler):
  def post(self):
    email = self.request.get("email")
    name = self.request.get("name")
    topics = self.request.get("topics")
    city = self.request.get("city")
    maxAttendees = self.request.get("maxAttendees")
    startDate = self.request.get("startDate")
    endDate = self.request.get("endDate")

    sender = "Conference Team <newmilktea@gmail.com>"
    to = "%s <%s>" % (name, email)
    subject = "You just host an amazing Conference"
    body = """
    Dear  %s,
    Following is the detail of your conference.
    Topics: %s,
    City: %s,
    MaxAttendees: %s,
    StartDate: %s,
    EndDate: %s.
    ----
    Have a nice day.
    From Conference Team.
    """ % (name,
           topics,
           city,
           maxAttendees,
           startDate,
           endDate)
    mail.send_mail(sender=sender, to=to, subject=subject, body=body)

app = webapp2.WSGIApplication([('/task/sendEmail', EmailApi)], debug=True)