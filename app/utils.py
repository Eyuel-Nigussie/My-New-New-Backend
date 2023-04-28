#password hashing
import smtplib #
from email.mime.text import MIMEText #
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(password: str):
    return pwd_context.hash(password)

def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def send_email(recipient: str, message: str):
    # Set up the email message
    msg = MIMEText(message)
    msg['Subject'] = 'Your recipe has been added!'
    msg['From'] = 'eyuthedev@gmail.com'
    msg['To'] = recipient

    # Connect to the SMTP server and send the email
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('eyuthedev@gmail.com', '14586300@cC')
        server.send_message(msg)