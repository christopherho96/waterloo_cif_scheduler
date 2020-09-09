from urllib import request
from bs4 import BeautifulSoup
from twilio.rest import Client
import os
import logging
import sys
import datetime

start_time = datetime.time(9,00) #9AM
end_time = datetime.time(19, 00) #7PM
now_time = datetime.datetime.now().time()
if not(start_time <= now_time <= end_time):
    logging.log(msg="Current time {} is outside of 9AM and 7PM. No web scrape required".format(now_time), level=30)
    sys.exit()

try:
    twilio_account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    twilio_auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    twilio_phone_number = os.environ["TWILIO_PHONE_NUMBER"]
    personal_phone_number = os.environ["PERSONAL_PHONE_NUMBER"]
    client = Client(twilio_account_sid, twilio_auth_token)
except Exception as e:
    logging.error(e)
    logging.error("Unable to access environment variables")
    sys.exit()

url = 'https://warrior.uwaterloo.ca/Program/GetProgramDetails?courseId=cc2a16d7-f148-461e-831d-7d4659726dd1&semesterId=b0d461c3-71ea-458e-b150-134678037221'
url_request = request.urlopen(url)
page_html = url_request.read()
url_request.close()
page_soup = BeautifulSoup(page_html, "html.parser")
schedule_cards = page_soup.findAll("div", {"class": "program-schedule-card"})
message = ""
for schedule_card in schedule_cards:
    try:
        date = schedule_card.find(attrs={'class': 'pull-left'}).text.strip()
        details = schedule_card.find('small').text.split("\n")
        time = details[1].strip()
        open_spots = details[3].strip()
        if open_spots != "No Spots Available":
            message += "\n{}\n{}\n{}\n".format(date, time, open_spots)
    except Exception as e:
        logging.error(e)
        logging.error("Error web scraping for each reservation detail on CIF schedule")
        sys.exit()

if message == "":
    message = "\nNo available gym reservations\n\n{}".format(url)
else:
    message += "\nBook CIF gym reservation now at\n\n{}".format(url)
try:
    if len(message) >= 1600:
        error = "Message is longer than 1600 characters. Click link to see CIF schedule\n\n {}".format(url)
        logging.error(error)
        client.messages.create(body=error, from_=twilio_phone_number, to=personal_phone_number)
    else:
        client.messages.create(body=message, from_=twilio_phone_number, to=personal_phone_number)
        logging.info("Successfully sent text")
except Exception as e:
    logging.error(e)
    logging.error("Error sending text message")
