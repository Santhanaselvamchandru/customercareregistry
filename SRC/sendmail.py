import sendgrid
from sendgrid.helpers.mail import *
import base64
def sendemail(user,subject,TEXT):
    api = sendgrid.SendGridAPIClient('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')
    from_email = Email('customercareregistry@gmail.com')
    to_email = To(user)
    content = Content('text/plain',TEXT)
    mail = Mail(from_email,to_email,subject,content)
    mail_json = mail.get()
    response = api.client.mail.send.post(request_body=mail_json)
    print(response.status_code)
    print(response.headers)
    