from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.utils import make_msgid
from bs4 import BeautifulSoup
import smtplib
import os
import requests
from email import encoders
from dotenv import load_dotenv
import sys

# Load environment variables from .env file.
load_dotenv()

sender_email =  os.environ.get('SENDER_EMAIL')
password = os.environ.get('PASSWORD')
server_domain = os.environ.get('SERVER')
test_receiver_emails = os.environ.get('TEST_RECEIVER_EMAILS')
# All environment variables are strings by default so I need to convert it to integer.
port = int(os.environ.get('PORT'))

worker_url = os.environ.get('WORKER_URL')

def get_receivers_emails():
    if len(sys.argv) > 1 and sys.argv[1] == '--production':
        response = requests.get(worker_url + '/email')
        receiver_emails = response.json()
    else: 
        receiver_emails = test_receiver_emails.split(',')
    
    # returns list of strings
    return receiver_emails

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

    # Add file as application/octet-stream
    # Email client can usually download this automatically as attachment
    attachment = MIMEBase("application", "vnd.openxmlformats-officedocument.wordprocessingml.document")
    attachment.set_payload(menu_file.content)

    # Encode file in ASCII characters to send by email    
    encoders.encode_base64(attachment)

    file_name = menu_link.split('/')[-1]

    # Add header as key/value pair to attachment part
    attachment.add_header(
        "Content-Disposition", "attachment",
        filename=file_name
    )

    html = f"""\
    <html>
    <body>
        <p>Ahoj, 
        <br>
        na strankách školky je nový článek => <strong>"{ header }"</strong>.
        </p> 

        <br>
        <p>
        <a href="{ link }">Článek na webu</a>
        </p>
    </body>
    </html>
    """
    send_email(html, attachment)

def send_email(html, attachment=None, ):
    receiver_emails = get_receivers_emails()
    for email in receiver_emails:
        message = MIMEMultipart()
        message["Subject"] = 'Novinky ze školky'
        message["From"] = sender_email
        message["To"] = email
        # Every message must have its own message id. This id is not stored just in the message.
        # This id is an unique identifier of the message.
        message["Message-Id"] = make_msgid()

        # Turn into html MIMEText objects
        part1 = MIMEText(html, "html")

        message.attach(part1)
        if attachment:
            message.attach(attachment)

        # Create secure connection with server and send email
        with smtplib.SMTP(server_domain, port) as server:
            server.starttls() 
            server.login(sender_email, password)
            server.sendmail(
                sender_email, email, message.as_string()
            )

        print(f"Odeslano na { email }.")