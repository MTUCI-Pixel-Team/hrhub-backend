import email
import imaplib
import smtplib
from email.header import decode_header
from email.mime.text import MIMEText

HR_EMAIL = 'jiopydryk011@yandex.ru'
HR_PASSWORD = 'tdigxyrpiliyyyqq'

def read_incoming_emails(email_user=HR_EMAIL, email_pass=HR_PASSWORD):
    mail = imaplib.IMAP4_SSL('imap.yandex.ru')
    mail.login(email_user, email_pass)
    mail.select('inbox')

    status, messages = mail.search(None, 'UNSEEN')
    for num in messages[0].split():
        status, data = mail.fetch(num, '(RFC822)')
        print('data')
        print(data)
        email_msg = data[0][1]
        msg = email.message_from_bytes(email_msg)

        # Получение темы сообщения
        subject = decode_header(msg["Subject"])[0][0]
        if isinstance(subject, bytes):
            subject = subject.decode()
        # Получение отправителя сообщения
        from_ = msg.get("From")
        print(f"Subject: {subject}")
        print(f"From: {from_}")

        # Если сообщение многочастное, получаем тело сообщения
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    print(f"Body: {body}")
                    break
        else:
            print('Сообщение не удалось декодировать')
        

    mail.logout()

# Замените 'your_email@yandex.ru' и 'your_password' на ваши данные для входа
read_incoming_emails()

def send_email(subject, message, to_addr, from_addr=HR_EMAIL, password=HR_PASSWORD):
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = to_addr

    with smtplib.SMTP_SSL('smtp.yandex.ru', 465) as server:
        server.login(from_addr, password)
        server.sendmail(from_addr, to_addr, msg.as_string())
        print("Письмо успешно отправлено")

# send_email('Тестовое сообщение', 'Это тестовое сообщение.', 'dofskela@gmail.com')