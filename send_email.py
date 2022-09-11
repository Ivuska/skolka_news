from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import make_msgid
from urllib import request
from bs4 import BeautifulSoup
import smtplib
import os
import requests

sender_email =  os.environ.get('SENDER_EMAIL')
# Email addresses must be separated by comma then it works for multiple addresses.
receiver_emails = os.environ.get('RECEIVER_EMAILS')
password = os.environ.get('PASSWORD')
server_domain = os.environ.get('SERVER')
# All environment variables are strings by default so I need to convert it to integer.
port = int(os.environ.get('PORT'))

def send_email_with_content(header, link, content):
    # Create the HTML version of your message
    html = f"""\
    <html>
    <body>
        <p>Ahoj, 
        <br>
        na strankách školky je nový článek => <strong>"{ header }"</strong>.</p> 

        <br>
        <p>
        { content }
        </p>

        <br>
        <p>
        <a href="{ link }">Článek na webu</a>
        </p>
    </body>
    </html>
    """
    send_email(html)

def send_email_with_content_to_download(header, link, content):
    # Create the HTML version of your message
    html_content = content
    soup = BeautifulSoup(html_content, 'html.parser')
    # There are two links in the article, both with the link to download the menu, so I can scrape the first one and do not specify it more.
    menu_link = soup.find("a").get("href")
    print(menu_link)
    menu_file = requests.get(menu_link)
    open("jidelnicek.docx", "wb").write(menu_file.content)
    html = f"""\
    <html>
    <body>
        <p>Ahoj, 
        <br>
        na strankách školky je nový článek => <strong>"{ header }"</strong>.
        </p> 

        <br>
        <p>
        <a href="{ menu_link }"><strong>STÁHNOUT JÍDELNÍČEK</strong></a>
        </p>

        <br>
        <p>
        <a href="{ link }">Článek na webu</a>
        </p>
    </body>
    </html>
    """
    send_email(html)

def send_email(html):
    message = MIMEMultipart()
    message["Subject"] = 'Novinky ze školky'
    message["From"] = sender_email
    message["To"] = receiver_emails
    # Every message must have its own message id. This id is not stored just in the message.
    # This id is an unique identifier of the message.
    message["Message-Id"] = make_msgid()

    # Turn into html MIMEText objects
    part1 = MIMEText(html, "html")
    message.attach(part1)

    # Create secure connection with server and send email
    with smtplib.SMTP(server_domain, port) as server:
        server.starttls() 
        server.login(sender_email, password)
        server.sendmail(
            # I need to create a list of receiver email addresses.
            sender_email, receiver_emails.split(","), message.as_string()
        )

    print("Odeslano")