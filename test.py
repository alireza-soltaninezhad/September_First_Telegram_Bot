import smtplib
from email.message import EmailMessage

# Define your email parameters
smtp_server = 'smtp.porkbun.com' # Replace with your Porkbun SMTP server
smtp_port = 587 # or 465 if using SSL
smtp_username = 'support@septemberfirst.org' # Replace with your Porkbun email address
smtp_password = '#Septemberfirst2023' # Replace with your email password

# Create an EmailMessage object
message = EmailMessage()
message.set_content('This is the body of the email')
message['Subject'] = 'Subject of the email'
message['From'] = smtp_username
message['To'] = 'ar.soltaninezhad@gmail.com' # Replace with recipient's email address

# Connect to the SMTP server
with smtplib.SMTP(smtp_server, smtp_port) as server:
    server.starttls() # You can use server.login() if using SSL
    server.login(smtp_username, smtp_password)
    server.send_message(message)

print('Email sent successfully!')
