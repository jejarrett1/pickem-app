from app import mail
from flask import render_template, current_app
from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart




def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    mailserver = SMTP(current_app.config['MAIL_SERVER'], 587)
    mailserver.ehlo()
    mailserver.starttls()
    mailserver.login(current_app.config['MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'])


    msg = MIMEMultipart('alternative')
    msg['To']=', '.join(recipients)
    msg['From']=sender
    msg['Subject']=subject

    text = MIMEText(text_body, 'plain')
    html = MIMEText(html_body, 'html')
    msg.attach(text)
    msg.attach(html)


    mailserver.sendmail(sender, recipients, msg.as_string())

    mailserver.quit()



