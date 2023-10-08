from django.core.mail import send_mail, mail_admins, BadHeaderError, EmailMessage
from django.shortcuts import render
from templated_mail.mail import BaseEmailMessage

# Create your views here.
def say_hello(request):
    try:
        message = BaseEmailMessage(
            template_name='emails/hello.html',
            context={'name': 'Yi'}
        )
        message.send(['john@yiyang.com'])
        # message = EmailMessage('subject', 'message', 'from@yiyang.com', ['john@yiyang.com'])
        # message.attach_file('playground/static/images/photo.jpg')
        # message.send()
        # mail_admins('subject', 'message', html_message='message')
        # send_mail('subject', 'message', 'info@yiyang.com', ['bob@yiyang.com'])
    except BadHeaderError:
        pass
    return render(request, 'hello.html')