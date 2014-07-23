import webapp2
from google.appengine.api import mail

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