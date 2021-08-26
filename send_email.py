import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

def send_me_email(header, link, content):
    sender_email = os.environ.get('SENDER_EMAIL')
    if not sender_email:
        password = input('Type sender address:')
    receiver_email = os.environ.get('RECEIVER_EMAIL')
    if not receiver_email:
        password = input('Type receiver address:')
    password = os.environ.get('PASSWORD')
    if not password:
        password = input('Type your password:')

    message = MIMEMultipart("alternative")
    message["Subject"] = 'Novinky ze školky'
    message["From"] = sender_email
    message["To"] = receiver_email

    # Create the plain-text and HTML version of your message
    text = f'Ahoj, na strankách školky je nový článek {header}. Víc najdeš na {link}.'
    html = f"""\
    <html>
    <body>
        <p>Ahoj, na strankách školky je nový článek <strong>{header}</strong> Víc najdeš na <a href="{link}"><strong>TADY</strong></a>.</p>
        {content}
    </body>
    </html>
    """

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    # Create secure connection with server and send email
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls() 
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )

    print("Odeslano")