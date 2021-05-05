import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
import base64
def sendemail(user,subject,TEXT):
    api = sendgrid.SendGridAPIClient('Your API')
    from_email = Email('Your Mail')
    to_email = To(user)
    content = Content('text/plain',TEXT)
    mail = Mail(from_email,to_email,subject,content)
    mail_json = mail.get()
    response = api.client.mail.send.post(request_body=mail_json)
    