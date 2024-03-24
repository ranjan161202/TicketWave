import requests
from main import celery,cache
from datetime import datetime, timedelta, date
from application.models import *  # Update with your actual models
from application.database import db
from jinja2 import Template
import os
import csv
from weasyprint import HTML
from mail_config import send_email

@celery.on_after_finalize.connect
def setup_intervalTASK(sender, **kwargs):
    sender.add_periodic_task(
        # Send a remainder at 5:30pm IST of every day
        # crontab(minute=30, hour=17),
        10,
        send_reminder_webhooks.s(), name="Daily reminder"
    )

    sender.add_periodic_task(
        # Send the monthly report at 5:30pm IST of every month
        # crontab(minute=30, hour=17, day_of_month=25),
        10,
        send_monthly_reports.s(), name="Monthly Report"
    )


@celery.task(name='tasks.send_reminder_webhooks')
def send_reminder_webhooks():
    yesterday = datetime.now() - timedelta(days=1)
    inactive_users = Users.query.filter(Users.lastAct < yesterday).all()
    
    for user in inactive_users:
        if user.lastAct is None:
            continue  # Skip users without activity data
        
        webhook_url = "https://chat.googleapis.com/v1/spaces/AAAA30cocDE/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=7QghOKWISpBOYN02NveeyiCJ_dVKs1KZt3fRmocjU9M"  # Update with your actual webhook URL
            
        payload = {
            "text": f"{user.userName}Please visit our site or book a ticket!",
        }
        
        response = requests.post(webhook_url, json=payload)
        print(response.status_code)
        if response.status_code == 200:
            # user.last_reminder_sent = datetime.now()
            # db.session.commit()
            print("Success")


@celery.task()
def send_monthly_reports():
    users = Users.query.all()
    for user in users:
        if user.userName == 'admin':
            continue
        user_bookings = userBookings.query.filter_by(userID=user.userID).all()
        if(len(user_bookings)==0):
            continue
        print(user_bookings)
        month = date.today().strftime("%B")
        e = user.userName+'@gmail.com'
        u = {'logged': user.lastAct, 'email': e}
        u['username'] = user.userName

        filepath = f"static/monthly_reports/monthly_report_{str(u['username'])}.pdf"

        # Check if folder is not present then create one
        if not os.path.exists('static/monthly_reports/'):
            os.mkdir(path='static/monthly_reports/')

        with open(r"templates/monthly_report.html") as file:
            msg_template = Template(file.read())
        with open(r"templates/pdf.html") as file:
            pdf_template = Template(file.read())

        booking_info_text = []
        for booking in user_bookings:
            movie_showing = MovieShowings.query.get(booking.movieShowingID)
            booking_info = {
                'bookingID': booking.bookingID,
                'movieName': Movies.query.get(movie_showing.movieID).movieName,
                'theatreName': Theatres.query.get(movie_showing.theatreID).theatreName,
                'movieDate': MovieDates.query.get(movie_showing.movieDateID).movieDate,
                'movieTime': MovieTimes.query.get(movie_showing.movieTimeID).movieTime,
                'numTickets': booking.numTickets
            }
            booking_info_text.append(booking_info)
        print(booking_info_text)
        booking_info = booking_info_text
        pdf_html = HTML(string=pdf_template.render(user=u, booking_info=booking_info, month=month))
        pdf_html.write_pdf(target=filepath)
        send_email(to=e, subject="Monthly report", attachment=filepath,msg=msg_template.render(username=u['username']))
    return 'sucess'



@celery.task()
@cache.memoize(timeout=15)
def exTheatre(tid: int):
    theatre_data = Theatres.query.filter_by(theatreID=tid).first()
    theatre_shows = MovieShowings.query.filter_by(theatreID=tid).all()
    theatre_bookings_count = userBookings.query.filter(
        userBookings.movieShowingID.in_([show.movieShowingID for show in theatre_shows])
    ).all()

    email = "raghav42513@gmail.com"
    filepath = 'static/download/' + theatre_data.theatreName + '.csv'

    with open(r"templates/download.html") as file:
        msg_template = Template(file.read())

    if not os.path.exists('static/download/'):
        os.mkdir(path='static/download/')

    # Create the CSV file
    with open(file=filepath, mode='w') as file:
        csv_obj = csv.writer(file, delimiter=',')
        csv_obj.writerow(['Theatre Name', 'Location', 'Number of Shows', 'Number of Bookings'])
        csv_obj.writerow([theatre_data.theatreName, theatre_data.location, len(theatre_shows), len(theatre_bookings_count)])

    send_email(to=email, subject="CSV file for the theatre " + theatre_data.theatreName,
               msg=msg_template.render(username='Admin', theatre=theatre_data.theatreName), attachment=filepath)
    
    return 'success'