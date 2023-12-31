import os
import re
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, CallbackContext, ConversationHandler, MessageHandler, Filters
from datetime import datetime
import threading
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from multiprocessing import Process
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle
from google.auth.transport.requests import Request
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.message import EmailMessage
import smtplib
from datetime import datetime, timedelta
import pytz
from jdatetime import date as jdate
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from sqlalchemy import and_
from flask_apscheduler import APScheduler
import pytz
from datetime import timedelta
import jdatetime

SCOPES = ['https://www.googleapis.com/auth/calendar']
scheduler = APScheduler()



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

TIME, AVAILABILITY, NAME, PHONE, GOAL, EMAIL, SOP, COUNTRY, AGE, EDUCATION, CONFIRM, MARRIED_STATUS, MILITARY_SERVICE, WORKING_EXPERIENCE, LANGUAGE_CERTIFICATE = range(15)


smtp_server = 'smtp.porkbun.com'
smtp_port = 587
smtp_username = 'support@septemberfirst.org'
smtp_password = '#Septemberfirst2023'

# Define your models
class ServiceProvider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)


class Availability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('service_provider.id'), nullable=False)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    availability_type = db.Column(db.String(50), nullable=False)  # Added this line
    service_provider = db.relationship('ServiceProvider', backref=db.backref('availabilities', lazy=True))


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('service_provider.id'), nullable=False)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)


# def get_calendar_service():
#     creds = None
#     # The file token.pickle stores the user's access and refresh tokens, and is
#     # created automatically when the authorization flow completes for the first
#     # time.
#     if os.path.exists('token.pickle'):
#         with open('token.pickle', 'rb') as token:
#             creds = pickle.load(token)
#     # If there are no (valid) credentials available, let the user log in.
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 'client_secret.json', SCOPES)
#             creds = flow.run_local_server(port=8080)  # Specify a fixed port number
#         # Save the credentials for the next run
#         with open('token.pickle', 'wb') as token:
#             pickle.dump(creds, token)
#
#     try:
#         service = build('calendar', 'v3', credentials=creds)
#         return service
#     except Exception as e:
#         print(e)
#         return None



def convert_and_subtract_60_mins(dt_obj):

    amsterdam_tz = pytz.timezone('Europe/Amsterdam')
    dt_obj = amsterdam_tz.localize(dt_obj)


    tehran_tz = pytz.timezone('Asia/Tehran')
    dt_obj_tehran = dt_obj.astimezone(tehran_tz)


    dt_obj_tehran -= timedelta(minutes=0)


    dt_obj_jalali = jdate.fromgregorian(
        year=dt_obj_tehran.year,
        month=dt_obj_tehran.month,
        day=dt_obj_tehran.day
    )

    persian_datetime_str = f"{dt_obj_jalali.strftime('%Y-%m-%d')}, {dt_obj_tehran.strftime('%H:%M:%S')}"

    return persian_datetime_str

def send_email(user_data):

    provider_name = user_data['provider_name']
    availability_type = user_data['availability_type']
    meet_link = ''
    if provider_name.lower() == 'amin':
        meet_link = 'https://meet.google.com/cyw-dhay-tsm'
    if provider_name.lower() == 'mahdis':
        meet_link = 'https://meet.google.com/fsd-mqrb-aas?hs=187&authuser=0&ijlm=1693426810041&adhoc=1'
    if provider_name.lower() == 'alireza':
        meet_link = 'https://meet.google.com/vbu-temi-wwz'
    if provider_name.lower() == 'maryam':
        meet_link = 'https://meet.google.com/tjt-whuc-ybs'

    print(availability_type)
    print(provider_name)

    if availability_type == 'Consultation':
        body = f"""\
        <!DOCTYPE html>
        <html dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>Appointment Confirmation</title>
            <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {{
                    font-family: 'Tahoma', sans-serif;
                    background-color: #fafafa;
                }}
                .container {{
                    direction: rtl;
                    margin: 30px auto;
                    padding: 20px;
                    border: 2px solid #ccc;
                    border-radius: 10px;
                    background-color: #ffffff;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                }}
                .highlight {{
                    font-weight: bold;
                    color: #2c3e50;
                }}
                .text-primary {{
                    color: #007bff;
                }}
                .text-secondary {{
                    color: #6c757d;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <span class="highlight">{user_data['name']}</span> عزیز،
                <br><br>
                درخواستت رو دریافت کردیم و خوشحالیم که قراره تجربیات‌مون رو باهم به اشتراک بگذاریم!
                <br><br>
                لینک گوگل میت: <span class="highlight">{meet_link}</span>
                <br>
                تاریخ و زمان شروع گپ و گفت به وقت آمستردام: <span class="highlight text-primary">{user_data['start_time']}</span>
                <br>
                تاریخ و زمان اتمام گپ و گفت به وقت آمستردام: <span class="highlight text-primary">{user_data['end_time']}</span>
                <br>
                تاریخ و زمان گپ و گفت به وقت تهران: <span class="highlight text-secondary">{convert_and_subtract_60_mins(user_data['start_time'])}</span>
                <br>
                تاریخ و زمان گپ و گفت به وقت تهران: <span class="highlight text-secondary">{convert_and_subtract_60_mins(user_data['end_time'])}</span>                
                <br><br>
                <strong>مشخصاتی که برامون ثبت کردی از قراره زیره:</strong>
                <br>
                نام: <span class="highlight">{user_data['name']}</span>
                <br>
                شماره تلگرام: <span class="highlight">{user_data['phone']}</span>
                <br>
                سن: <span class="highlight">{user_data['age']}</span>
                <br>
                قصد داری از این گپ‌وگفت: <span class="highlight">{user_data['goal']}</span>
                <br>
                آدرس ایمیل: <span class="highlight">{user_data['email']}</span>
                <br>
                هدفت از مهاجرت کردن چیه؟ <span class="highlight">{user_data['sop']}</span>
                <br>
                خلاصه کوتاه از وضعیت تحصیلی: <span class="highlight">{user_data['education']}</span>
                <br>
                خلاصه کوتاه از وضعیت کاری: <span class="highlight">{user_data['working_experience']}</span>
                <br>
                وضعیت و سطح زبان: <span class="highlight">{user_data['language_certificate']}</span>
                <br>
                کشور های مورد نظر برای مهاجرت: <span class="highlight">{user_data['country']}</span>
                <br>
                وضعیت تاهل: <span class="highlight">{user_data['married_status']}</span>
                <br>
                وضعیت نظام وظیفه: <span class="highlight">{user_data['military_service']}</span>
                <br><br>
                لطفا در صورت امکان عدم حضور در جلسه گپ و گفت، ۲۴ ساعت قبل با ریپلای به همین ایمیل به ما اطلاع بده.
                <br><br>
                ممنون که بهمون کمک‌ می‌کنی که بهت کمک کنیم!
                <br>
                ارادتمند،
                <br>
                تیم ایستگاه یکم
            </div>
        </body>
        </html>
        """
    else:
        body = f"""\
        <!DOCTYPE html>
        <html dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>Appointment Confirmation</title>
            <style>
                body {{
                    font-family: 'Tahoma', sans-serif;
                }}
                .container {{
                    direction: rtl;
                    margin: 20px;
                    padding: 20px;
                    border: 1px solid #ccc;
                    border-radius: 10px;
                    background-color: #f9f9f9;
                }}
                h3, h4 {{
                    color: #34495e;
                }}
                ul {{
                    list-style-type: disc;
                    padding-inline-start: 40px;
                }}
                .highlight {{
                    font-weight: bold;
                    color: #2c3e50;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h3><span class="highlight">{user_data['name']}</span> عزیز،</h3>
                <p>درخواستت رو دریافت کردیم و خوشحالیم که قراره تجربیات‌مون رو باهم به اشتراک بگذاریم!</p>
                <p>لطفا اگر لازمه مدارکت رو بازخوانی کنیم، روی همین ایمیل ریپلای بزن و اونارو پیوست کن.</p>
                <p>از طریق این ایمیل با <span class="highlight">{provider_name}</span> در ارتباط خواهی بود!</p>

                <h4>مشخصاتی که برامون ثبت کردی از قراره زیره:</h4>
                <ul>
                    <li>نام: <span class="highlight">{user_data['name']}</span></li>
                    <li>شماره تلگرام: <span class="highlight">{user_data['phone']}</span></li>
                    <li>سن: <span class="highlight">{user_data['age']}</span></li>
                    <li>قصد داری از این گپ‌وگفت: <span class="highlight">{user_data['goal']}</span></li>
                    <li>آدرس ایمیل: <span class="highlight">{user_data['email']}</span></li>
                    <li>هدفت از مهاجرت کردن چیه؟ <span class="highlight">{user_data['sop']}</span></li>
                    <li>خلاصه کوتاه از وضعیت تحصیلی: <span class="highlight">{user_data['education']}</span></li>
                    <li>خلاصه کوتاه از وضعیت کاری: <span class="highlight">{user_data['working_experience']}</span></li>
                    <li>وضعیت و سطح زبان: <span class="highlight">{user_data['language_certificate']}</span></li>
                    <li>کشور های مورد نظر برای مهاجرت: <span class="highlight">{user_data['country']}</span></li>
                    <li>وضعیت تاهل: <span class="highlight">{user_data['married_status']}</span></li>
                    <li>وضعیت نظام وظیفه: <span class="highlight">{user_data['military_service']}</span></li>
                </ul>

                <p>ممنون که بهمون کمک‌ می‌کنی که بهت کمک کنیم!</p>

                <p>ارادتمند،<br>
                تیم ایستگاه یکم</p>
            </div>
        </body>
        </html>
        """


    # Create an EmailMessage object
    message = MIMEMultipart()
    # message.set_content(body)
    html = MIMEText(body, "html")
    message.attach(html)
    message['Subject'] = "New Appointment"
    message['From'] = smtp_username
    message['To'] = user_data['email']

    # Connect to the SMTP server
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(message)

    print('Email sent successfully to user!')



    if availability_type == 'Consultation':
        body2 = f"""\
            Dear {provider_name},

            We have received a new request for {availability_type}.

            Ttime for {availability_type} is between {user_data['start_time']} and {user_data['end_time']} in central european time 
            Time for {availability_type} is between  {convert_and_subtract_60_mins(user_data['start_time'])} and {convert_and_subtract_60_mins(user_data['end_time'])} in Tehran Time.
            The Google Meet Link: {meet_link}
            Here are the details that the client provided us:

            - Name: {user_data['name']}
            - Type of Appointment: {availability_type}
            - Phone (Telegram Number): {user_data['phone']}
            - Age: {user_data['age']}
            - Goal of making Appointment: {user_data['goal']}
            - Email: {user_data['email']}
            - Goal of Migration: {user_data['sop']}
            - Education Status: {user_data['education']}
            - Working Experience: {user_data['working_experience']}
            - Aim Countries: {user_data['country']}
            - Married Status: {user_data['married_status']}
            - Military Service Status: {user_data['military_service']}
            - Language Certificate: {user_data['language_certificate']}

            Thanks for your time.

            Best regards,
            First September Support
            """
    else:
        body2 = f"""\
            Dear {provider_name},

            We have received a new request for {availability_type}.
            We asked the clint to send the required documents as a reply to this email at September First official email.

            Here are the details that the client provided us:

            - Name: {user_data['name']}
            - Type of Appointment: {availability_type}
            - Phone (Telegram Number): {user_data['phone']}
            - Age: {user_data['age']}
            - Goal of making Appointment: {user_data['goal']}
            - Email: {user_data['email']}
            - Goal of Migration: {user_data['sop']}
            - Education Status: {user_data['education']}
            - Working Experience: {user_data['working_experience']}
            - Aim Countries: {user_data['country']}
            - Married Status: {user_data['married_status']}
            - Military Service Status: {user_data['military_service']}
            - Language Certificate: {user_data['language_certificate']}

            Thanks for your time.

            Best regards,
            First September Support
            """
    # Create an EmailMessage object
    message2 = EmailMessage()
    message2.set_content(body2)
    # text = MIMEText(body2, "plain", "utf-8")
    # message2.attach(text)
    message2['Subject'] = "New Appointment"
    message2['From'] = smtp_username


    if provider_name.lower()=='amin':
        message2['To'] = 'aminsinichi@gmail.com'
    if  provider_name.lower()=='maryam':
        message2['To'] = 'isf.torabimaryam@gmail.com'
    if  provider_name.lower()=='mahdis':
        message2['To'] = 'smmahdis2080@gmail.com'
    if  provider_name.lower()=='alireza':
        message2['To'] = 'ar.soltaninezhad@gmail.com'
    # Connect to the SMTP server
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # You can use server.login() if using SSL
        server.login(smtp_username, smtp_password)
        server.send_message(message2)





def start(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['ادامه', 'انصراف']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text(
        'سلام، به بات تلگرام پادکست «یکم سپتامبر» خوش اومدی! \nاز طریق این بات می‌تونی به طرح «ایستگاه یکم» دسترسی داشته باشی. \nدر این طرح، تیمی متشکل از افرادی با پیشینه‌های مختلف دور هم جمع شدند و می‌تونی به شکل کاملا رایگان و بدون واسطه باهاشون در ارتباط باشی. \nهر کدوم از اعضای تیم ما چیزهای محدودی می‌دونند و مشتاق هستند که این دانسته‌های از جنس تجربه رو در مورد مهاجرت باهات در میون بذارن. برای اینکه مناسب‌ترین فرد رو انتخاب کنی، \n\nحتما یک سری به وبسایت ما بزن و بخش «حیطه‌های تسلط تیم ما» رو دقیق مطالعه کن، بعدش به بات تلگرام برگرد و روی کلید «ادامه» در زیر کلیک کن. \n وبسایت ما:  septemberfirst.org \n  \nاگر اشکالی در حین استفاده از بات پیش اومد لطفا مارو مطلع کن تا خیلی زود بهش رسیدگی کنیم:\n  support@septemberfirst.org \n اگر به هر دلیلی بات دچار مشکل شد و یا هرجا که خواستی بات رو متوقف کنی و از اول فرایند رو شروع کنی، کافیه روی /stop کلیک کنی، سپس برای راه‌اندازی مجدد بات روی /start کلیک کن.',

        reply_markup=markup
    )
    return TIME

def stop(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "بات متوقف شد و با ارسال مجدد /start میتونی مجدد بات رو راه‌اندازی کنی!",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def time(update: Update, context: CallbackContext) -> int:
    user_response = update.message.text
    if user_response.lower() == 'ادامه':
        return availability(update, context)  # Call the availability function
    else:
        update.message.reply_text('قبوله، هروقت خواستی از بات استفاده کنی کافیه /start رو تایپ کنی.')
        return ConversationHandler.END


def sop(update: Update, context: CallbackContext) -> int:
    context.user_data['sop'] = update.message.text
    update.message.reply_text('برای چه کشورهایی قصد اپلای کردن داری؟ ')
    return COUNTRY

def country(update: Update, context: CallbackContext) -> int:
    context.user_data['country'] = update.message.text
    update.message.reply_text('لطفا سنت رو به عدد وارد کن:')
    return AGE

def age(update: Update, context: CallbackContext) -> int:
    context.user_data['age'] = update.message.text
    update.message.reply_text('کوتاه از پیشینه‌ی تحصیلی‌ات برامون بنویس:')
    return EDUCATION

def education(update: Update, context: CallbackContext) -> int:
    context.user_data['education'] = update.message.text
    update.message.reply_text('وضعیت تاهل‌ات رو بنویس:')
    return MARRIED_STATUS


def name(update: Update, context: CallbackContext) -> int:
    context.user_data['name'] = update.message.text
    update.message.reply_text('شماره تماست به انگلیسی رو وارد کن (ترجیحا شماره‌ای که باهاش تلگرام داری)')
    return PHONE


def phone(update: Update, context: CallbackContext) -> int:
    context.user_data['phone'] = update.message.text
    update.message.reply_text('قصد داری ازین گپ‌وگفت یا ارزیابی مدارکت چی عایدت بشه؟ \nاز انتظاراتی که داری برامون بنویس: ')
    return GOAL


def goal(update: Update, context: CallbackContext) -> int:
    context.user_data['goal'] = update.message.text
    update.message.reply_text('ایمیلی که بهش دسترسی داری رو دقیق وارد کن. \nدقت کن که ما از طریق این ایمیل باهات در ارتباط خواهیم بود، و مدارکت هم از همین طریق می‌تونی به دستمون برسونی (در حال حاضر بات ازین قابلیت پشتیبانی نمی‌کنه و نمی‌تونی فایل‌هاتو اینجا پیوست کنی): \n\n\n لطفا از صحت ایمیل آدرس اطمینان مجدد حاصل کنید!')
    return EMAIL

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")


def email(update: Update, context: CallbackContext) -> int:
    user_email = update.message.text
    if not EMAIL_REGEX.match(user_email):
        update.message.reply_text('ایمیلی که وارد کردی صحیح نبود، لطفا بررسیش کن و مجدد ایمیل صحیح رو وارد کن:')
        return EMAIL
    else:
        context.user_data['email'] = user_email
        update.message.reply_text('هدفت از مهاجرت کردن چیه؟\n قصد داری تحصیلی اقدام کنی، کاری یا روش‌های دیگه؟ \nقصد داری توی کشور مقصد بمونی (اقامت بگیری؟). \nاینجا اینطور نکاتی که می‌تونه به ما در فهم هدفت از مهاجرت کمک کنه رو در قالب یک پیام بنویس: ')
        return SOP


def married_status(update: Update, context: CallbackContext) -> int:
    context.user_data['married_status'] = update.message.text
    update.message.reply_text('از وضعیت نظام‌ وظیفه‌ات بنویس (اگر این سوال در موردت صدق می‌کنه):')
    return MILITARY_SERVICE

def military_service(update: Update, context: CallbackContext) -> int:
    context.user_data['military_service'] = update.message.text
    update.message.reply_text('کوتاه از پیشینه‌ی کاری‌ات برامون بنویس: ')
    return WORKING_EXPERIENCE

def working_experience(update: Update, context: CallbackContext) -> int:
    context.user_data['working_experience'] = update.message.text
    update.message.reply_text('اگر مدرک زبان داری یا اگر سطح زبان حدودی‌ات رو می‌دونی برامون بنویس:')
    return LANGUAGE_CERTIFICATE

def language_certificate(update: Update, context: CallbackContext) -> int:
    context.user_data['language_certificate'] = update.message.text
    update.message.reply_text('اگر قصد داری این درخواست رو ثبت کنی روی /confirm کلیک کن، در غیر این صورت برای کنسل کردنش روی /cancel کلیک کن دقت کن که ممکنه قدری طول بکشه تا ایمیل رو دریافت کنی، لطفا بیش از یکبار روی confirm کلیک نکن و منتظر بمون!')
    return CONFIRM



# def create_event(start_time, end_time, user_data):
#     try:
#         flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
#         creds = flow.run_local_server(port=8080)
#         service = build('calendar', 'v3', credentials=creds)
#
#         start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%S")
#         end_time_str = end_time.strftime("%Y-%m-%dT%H:%M:%S")
#
#         summary = user_data['name']
#         description = f"Name: {user_data['name']}\nPhone: {user_data['phone']}\nGoal: {user_data['goal']}\nEmail: {user_data['email']}\nStatement of Purpose: {user_data['sop']}\nAim Countries: {user_data['country']}\nAge: {user_data['age']}\nLast Education Certificate: {user_data['education']}"
#
#         event = {
#             'summary': summary,
#             'description': description,
#             'start': {
#                 'dateTime': start_time_str,
#                 'timeZone': 'Europe/Amsterdam',  # Timezone of the provider
#             },
#             'end': {
#                 'dateTime': end_time_str,
#                 'timeZone': 'Europe/Amsterdam',  # Timezone of the provider
#             },
#             'attendees': [
#                 {'email': user_data['email']},  # User's email
#             ],
#             'reminders': {
#                 'useDefault': False,
#                 'overrides': [
#                     {'method': 'email', 'minutes': 24 * 60},
#                     {'method': 'popup', 'minutes': 10},
#                 ],
#             },
#         }
#
#         event = service.events().insert(calendarId='primary', body=event).execute()
#
#         print(f'Event created: {event["htmlLink"]}')
#     except Exception as e:
#         print(f'An error occurred while creating the event: {e}')


# def confirm(update: Update, context: CallbackContext) -> int:
#     context.user_data['confirmation'] = update.message.text
#     update.message.reply_text('ممنون ازینکه وقت گذاشتی! \nایمیلت رو چک کن، و اگر مدارکی قرار هست برامون بفرستی اونجا پیوست کن (جزئیاتش رو می‌تونی توی ایمیل بخونی). \nبه زودی باهات در ارتباط خواهیم بود! \nاگر قصد داری مجدد از بات در آینده استفاده کنی، کافیه روی /start کلیک کنی. ',
#                               reply_markup=ReplyKeyboardRemove())
#     send_email(context.user_data)
#     # create_event(context.user_data['start_time'], context.user_data['end_time'], context.user_data)
#
#     # If user confirms, create an Appointment and delete the availability
#     if context.user_data['confirmation'] == "/confirm":
#         with app.app_context():
#             # Delete the availability
#             availability = Availability.query.get(context.user_data['availability_id'])  # Use availability_id
#             if availability:
#                 db.session.refresh(availability)  # Refresh the availability object before deleting
#                 db.session.delete(availability)
#                 db.session.commit()
#
#             # Create the appointment
#             appointment = Appointment(user_id=update.effective_user.id,
#                                       provider_id=context.user_data['provider_id'],
#                                       start_time=context.user_data['start_time'],
#                                       end_time=context.user_data['end_time'])
#             db.session.add(appointment)
#             db.session.commit()
#     return ConversationHandler.END

# def confirm(update: Update, context: CallbackContext) -> int:
#     context.user_data['confirmation'] = update.message.text
#     update.message.reply_text(
#         'ممنون ازینکه وقت گذاشتی! \nایمیلت رو چک کن، و اگر مدارکی قرار هست برامون بفرستی اونجا پیوست کن (جزئیاتش رو می‌تونی توی ایمیل بخونی). \nبه زودی باهات در ارتباط خواهیم بود! \nاگر قصد داری مجدد از بات در آینده استفاده کنی، کافیه روی /start کلیک کنی. \n اگر ایمیل تایید رو دریافت نکردی لطفا سریع به ما از طریق ایمیل زیر اطلاع بده که مشکل رو حل کنیم! \n  support@septemberfirst.org',
#         reply_markup=ReplyKeyboardRemove()
#     )
#
#     try:
#         send_email(context.user_data)
#     except Exception as e:
#         print(f"An error occurred while sending email: {e}")
#         # Optionally, inform the user that the email could not be sent
#         update.message.reply_text("An error occurred while sending the email. Please try again later.")
#
#     # create_event(context.user_data['start_time'], context.user_data['end_time'], context.user_data)
#
#     # If user confirms, create an Appointment and delete the availability
#     if context.user_data['confirmation'] == "/confirm":
#         with app.app_context():
#             # Delete the availability
#             availability = Availability.query.get(context.user_data['availability_id'])  # Use availability_id
#             if availability:
#                 db.session.refresh(availability)  # Refresh the availability object before deleting
#                 db.session.delete(availability)
#                 db.session.commit()
#
#             # Create the appointment
#             appointment = Appointment(
#                 user_id=update.effective_user.id,
#                 provider_id=context.user_data['provider_id'],
#                 start_time=context.user_data['start_time'],
#                 end_time=context.user_data['end_time']
#             )
#             db.session.add(appointment)
#             db.session.commit()
#
#     return ConversationHandler.END

from sqlalchemy.exc import IntegrityError
from telegram.ext import ConversationHandler, CallbackContext
from telegram import Update, ReplyKeyboardRemove


def confirm(update: Update, context: CallbackContext) -> int:
    context.user_data['confirmation'] = update.message.text

    if context.user_data['confirmation'] == "/confirm":
        with app.app_context():
            try:
                # Re-fetch the availability to make sure it still exists
                availability = Availability.query.get(context.user_data['availability_id'])
                if availability:
                    db.session.delete(availability)

                    appointment = Appointment(
                        user_id=update.effective_user.id,
                        provider_id=context.user_data['provider_id'],
                        start_time=context.user_data['start_time'],
                        end_time=context.user_data['end_time']
                    )
                    db.session.add(appointment)
                    db.session.commit()

                    try:
                        send_email(context.user_data)
                    except Exception as e:
                        print(f"An error occurred while sending email: {e}")
                        update.message.reply_text("An error occurred while sending the email. Please try again later.")

                    update.message.reply_text(
                        'ممنون ازینکه وقت گذاشتی! \nایمیلت رو چک کن، و اگر مدارکی قرار هست برامون بفرستی اونجا پیوست کن (جزئیاتش رو می‌تونی توی ایمیل بخونی). \nبه زودی باهات در ارتباط خواهیم بود! \nاگر قصد داری مجدد از بات در آینده استفاده کنی، کافیه روی /start کلیک کنی. \n اگر ایمیل تایید رو دریافت نکردی لطفا سریع به ما از طریق ایمیل زیر اطلاع بده که مشکل رو حل کنیم! \n  support@septemberfirst.org',
                        reply_markup=ReplyKeyboardRemove()
                    )
                else:
                    update.message.reply_text("The selected slot is no longer available. Please try another slot.")
            except IntegrityError:
                db.session.rollback()
                update.message.reply_text(
                    "متاسفانه همزمان با تو یکی برای این زمان اقدام کرده و درخواست رو زودتر از تو ثبت کرده! متاسفیم که باید روی /start کلیک کنی و یک زمان دیگه رو انتخاب کنی. می‌تونی پاسخ‌هایی که ارسال کردی رو دوباره برامون کپی کنی.")
    else:
        update.message.reply_text("You didn't confirm the appointment. To start over, click /start.")

    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    update.message.reply_text(
        'درخواستی که داشتی ثبت می‌کردی کنسل شد. \nاگر قصد داری مجدد بات رو راه‌اندازی کنی و درخواست جدیدی ثبت کنی کافیه روی /start کلیک کنی.  ',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    with app.app_context():
        availability_id = int(query.data)
        availability = Availability.query.get(availability_id)
        if availability:
            context.user_data['provider_id'] = availability.provider_id
            context.user_data['availability_id'] = availability.id  # Store availability_id
            context.user_data['start_time'] = availability.start_time
            context.user_data['end_time'] = availability.end_time
            context.user_data['provider_name'] = availability.service_provider.name
            context.user_data['availability_type'] = availability.availability_type
            if availability.start_time != None:
                # print(availability.start_time)
                query.edit_message_text(text=f"بازه زمانی انتخاب شد! \n شروع: {convert_and_subtract_60_mins(availability.start_time)} \n پایان:{convert_and_subtract_60_mins(availability.end_time)}")
            else:
                query.edit_message_text(text="درخواست شما برای بررسی مدارک و پرسیدن سوالات انتخاب شد.")
            update.effective_message.reply_text("در ادامه ما قراره یکسری سوال ازت بپرسیم که کمک‌مون میکنه دید بهتری ازت پیدا کنیم و دقیق‌تر کمکت کنیم. \n\n لطفا نامی که دوست داری باهاش خطابت کنیم رو وارد کن:")
            return NAME
        else:
            query.edit_message_text(text="متأسفیم، این بازه زمانی دیگر در دسترس نیست.")
            return ConversationHandler.END


def remove_expired_availability():
    with app.app_context():
        # Current time
        current_time = datetime.utcnow() + timedelta(minutes=120)

        # Calculate the time 12 hours from now (or 10 minutes for testing)
        time_threshold = current_time + timedelta(minutes=720)

        print(f"Current Time (UTC): {current_time}")
        print(f"Threshold Time (UTC): {time_threshold}")

        # Find availabilities that are too close to the current time
        soon_availabilities = Availability.query.filter(
            and_(
                Availability.start_time < time_threshold,
                Availability.start_time > current_time
            )
        ).all()

        print(f"Number of soon availabilities found: {len(soon_availabilities)}")

        for availability in soon_availabilities:
            print(f"Deleting availability with start_time: {availability.start_time}")
            db.session.delete(availability)

        # Commit changes to the database
        db.session.commit()




scheduler.add_job(
    id='remove_expired_availability_job',
    func=remove_expired_availability,
    trigger='interval',
    minutes=10,
    timezone=pytz.utc
)


def availability(update: Update, context: CallbackContext) -> int:
    with app.app_context():
        availabilities = db.session.query(Availability).options(db.joinedload(Availability.service_provider)).all()

    if availabilities:
        keyboard = [[InlineKeyboardButton(
            f"{availability.service_provider.name} :  {convert_and_subtract_60_mins(availability.start_time)} : {availability.availability_type}" if availability.start_time is not None else f"{availability.service_provider.name} : {availability.availability_type}",
            callback_data=str(availability.id))
        ] for availability in availabilities]

        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text(
            'در زیر می‌تونی ببینی هر کدوم از ما طی چند روز آینده چه زمان‌هایی به وقت ایران در دسترس هستیم.\n'
            ' اگر دوست داری با هرکدوم از ما وقت برای گپ‌وگفت تنظیم کنی، می‌تونی زمان‌هایی که پسوند Consultation داره رو انتخاب کنی.\n'
            'این گفت‌وگو به شکل یک تماس صوتی نهایت نیم ساعته خواهد بود. \n'
            'در صورتی که پرسش خاصی داری، یا قصد داری مدارکت بازخوانی بشه و ما نظر کلی‌مون رو راجع‌به بهبودش بدیم، گزینه‌ی  Check Documents and Ask Questions رو انتخاب کن. \n'
            'اسامی ما و زمان‌هایی که در دسترس هستیم هم قابل مشاهده است. \n'
            'ما هفته‌ به هفته‌ و گاهی حتی زودتر این زمان‌ها رو به روزرسانی می‌کنیم، بنابرین اگر در حال حاضر زمان مناسبی پیدا نمی‌کنی مجدد بهمون سر بزن! (برای اینکه ابتدا ربات رو /stop کن بعدا مجدد با /start راه اندازی کن). \n',
            reply_markup=reply_markup
        )
        return NAME  # Assuming NAME is defined elsewhere

    else:
        update.message.reply_text(
            "متاسفانه در حال حاضر هیچ کدوم از اعضای تیم ما در دسترس نیستند!\n "
            "ما هفته‌ به هفته‌ و گاهی حتی زودتر زمان‌های قابل دسترس‌مون رو به روزرسانی می‌کنیم، بنابرین اگر در حال حاضر زمان مناسبی پیدا نمی‌کنی مجدد بهمون سر بزن!\n "
            "برای راه‌اندازی مجدد بات، کافیه در آینده /start رو تایپ کنی.\n "
        )
        return ConversationHandler.END  # End the conversation if there are no available slots




def run_bot():
    updater = Updater("6194360753:AAFsu2Fm4DkfKGlowfUJTLW9A-0Zsv6FLww", use_context=True)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            TIME: [MessageHandler(Filters.regex('^(ادامه|انصراف)$'), time)],
            AVAILABILITY: [CommandHandler('availability', availability), CallbackQueryHandler(button)],
            NAME: [MessageHandler(Filters.text & ~Filters.command, name)],
            PHONE: [MessageHandler(Filters.text & ~Filters.command, phone)],
            GOAL: [MessageHandler(Filters.text & ~Filters.command, goal)],
            EMAIL: [MessageHandler(Filters.text & ~Filters.command, email)],
            SOP: [MessageHandler(Filters.text & ~Filters.command, sop)],
            COUNTRY: [MessageHandler(Filters.text & ~Filters.command, country)],
            AGE: [MessageHandler(Filters.text & ~Filters.command, age)],
            EDUCATION: [MessageHandler(Filters.text & ~Filters.command, education)],
            MARRIED_STATUS: [MessageHandler(Filters.text & ~Filters.command, married_status)],
            MILITARY_SERVICE: [MessageHandler(Filters.text & ~Filters.command, military_service)],
            WORKING_EXPERIENCE: [MessageHandler(Filters.text & ~Filters.command, working_experience)],
            LANGUAGE_CERTIFICATE: [MessageHandler(Filters.text & ~Filters.command, language_certificate)],
            CONFIRM: [CommandHandler('confirm', confirm), CommandHandler('cancel', cancel)]
        },
        fallbacks=[CommandHandler('cancel', cancel), CommandHandler('stop', stop)],

    )

    updater.dispatcher.add_handler(conv_handler)
    updater.dispatcher.add_handler(CommandHandler("stop", stop))
    updater.dispatcher.add_handler(CommandHandler("availability", availability))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/provider/availability', methods=['POST'])
def set_availability():
    provider_name = request.form['provider_name']
    availability_type = request.form['type_of_appointment']

    start_time = None
    end_time = None

    if availability_type == "Consultation":
        start_time = datetime.strptime(request.form['start_time'], "%Y-%m-%dT%H:%M")
        end_time = datetime.strptime(request.form['end_time'], "%Y-%m-%dT%H:%M")

    provider = ServiceProvider.query.filter_by(name=provider_name).first()

    if not provider:
        provider = ServiceProvider(name=provider_name)
        db.session.add(provider)
        db.session.commit()

    availability = Availability(provider_id=provider.id, start_time=start_time, end_time=end_time,
                                availability_type=availability_type)
    db.session.add(availability)
    db.session.commit()

    return 'Availability set successfully'


def run_app():
    with app.app_context():
        db.create_all()
    scheduler.init_app(app)
    scheduler.start()
    app.run(debug=False)



if __name__ == '__main__':
    # Process(target=function_name)
    bot_process = Process(target=run_bot)
    app_process = Process(target=run_app)

    # Start the new processes
    bot_process.start()
    app_process.start()

    # Wait for the processes to complete
    bot_process.join()
    app_process.join()

