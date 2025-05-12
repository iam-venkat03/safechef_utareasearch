from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os
import logging

def create_email(sender, recipients, subject, body, html_body=None):
    message = MIMEMultipart()
    message["From"] = sender
    message["To"] = ", ".join(recipients)
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))
    if html_body:
        message.attach(MIMEText(html_body, "html"))

    return message

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def send_email(smtp_server, port, sender, password, recipients, message):
    """Sends an email securely using SMTP_SSL."""
    try:
        with smtplib.SMTP_SSL(smtp_server, port) as server:
            server.login(sender, password)
            server.sendmail(sender, recipients, message.as_string())
            logging.info("Email sent successfully.")
    except Exception as e:
        logging.error(f"Error sending email: {e}")

# Add this to run the full script
if __name__ == "__main__":
    smtp_server = "smtp.gmail.com"
    port = 465
    sender_email = "safechef8@gmail.com"
    password = "xefc edqs sqiw rllf"  

    recipients = ["swaragreddy07@gmail.com"]
    subject = "Test Email from Python Script"
    body = "This is a plain text part of the email."
    html_body = "<h1>This is an HTML test</h1><p>Sent via <b>Python</b>!</p>"

    # Create and send the email
    email_msg = create_email(sender_email, recipients, subject, body, html_body)
    send_email(smtp_server, port, sender_email, password, recipients, email_msg)
