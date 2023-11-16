import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import schedule
import time
def send_notification(subject, message_html, recipients):
    # Email configuration
    sender_email = 'mahimatripathi0625@gmail.com'
    sender_password = 'fvhzimtbnbnhairi'
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587  # Port for Gmail SMTP
    
    # Create a multipart message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = ', '.join(recipients)

    # Create an HTML message
    message = MIMEText(message_html, 'html')

    # Attach the HTML message to the email
    msg.attach(message)

    try:
        # Connect to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)

        # Send the email
        server.sendmail(sender_email, recipients, msg.as_string())

        # Close the SMTP server
        server.quit()

        print("Email sent successfully.")
    except Exception as e:
        print(f"Email sending failed: {str(e)}")

# Usage example
if __name__ == "__main__":
    subject = "New Products Alert"
    recipients = ['naveen.jeena@vegease.in','harsh.goyal@vegease.in']

    # Example table HTML (replace this with your actual table HTML)
    table_html = """
   
    """

    # Your message containing the table HTML
    message_html = f"<p>{table_html}</p>"

    # Send the email
    send_notification(subject, message_html, recipients)
