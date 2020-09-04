from urllib import request
from bs4 import BeautifulSoup
from twilio.rest import Client
import os

twilio_account_sid = os.environ["TWILIO_ACCOUNT_SID"]
twilio_auth_token = os.environ["TWILIO_AUTH_TOKEN"]
twilio_phone_number = os.environ["TWILIO_PHONE_NUMBER"]
personal_phone_number = os.environ["PERSONAL_PHONE_NUMBER"]
client = Client(twilio_account_sid, twilio_auth_token)

url = 'https://warrior.uwaterloo.ca/Program/GetProgramDetails?courseId=cc2a16d7-f148-461e-831d-7d4659726dd1&semesterId=b0d461c3-71ea-458e-b150-134678037221'

uClient = request.urlopen(url)
page_html = uClient.read()
uClient.close()
page_soup = BeautifulSoup(page_html, "html.parser")

schedule_cards = page_soup.findAll("div", {"class": "program-schedule-card"})
message = ""
for schedule_card in schedule_cards:
    date = schedule_card.find(attrs={'class': 'pull-left'}).text.strip()
    details = schedule_card.find('small').text.split("\n")
    time = details[1].strip()
    open_spots = details[3].strip()
    message += "\n{}\n{}\n{}\n".format(date, time, open_spots)

message += "\nBook gym reservation now at https://warrior.uwaterloo.ca/Program/GetProgramDetails?courseId=cc2a16d7-f148-461e-831d-7d4659726dd1&semesterId=b0d461c3-71ea-458e-b150-134678037221 "
client.messages.create(body=message, from_=twilio_phone_number, to=personal_phone_number)
