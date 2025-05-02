import re
import speech_recognition as sr
import playsound
from gtts import gTTS
import os
import smtplib
import time
import imaplib
import email
from email.header import decode_header


# Function to convert text to speech
def speak(word):
    tts = gTTS(text=word, lang="en")
    filename = "voice.mp3"
    tts.save(filename)
    playsound.playsound(filename)
    os.remove(filename)

# Function to recognize speech input
def recognize_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            print(f"You said: {text}")
            return text.lower()
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return ""
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return ""

# Function to correct email input
def correct_email(email):
    email = email.lower()
    email = re.sub(r'\bat\b', '@', email)
    email = re.sub(r'\bdot\b', '.', email)
    email = re.sub(r'\btherate\b', '@', email)  # Catch incorrect recognition of "the rate" as "@" symbol
    email = re.sub(r'\s+', '', email)  # Remove any remaining whitespace

    # Ensure the email ends with a valid domain
    if not re.match(r'.+@.+\..+', email):
        speak("The email address seems incorrect. Please try again.")
        return ""
    return email

# Function to compose and send an email
def send_email(server, username):
    recipient = ""
    while not recipient:
        speak('Who is the recipient?')
        recipient = recognize_speech()
        recipient = correct_email(recipient)
    
    speak('What is the subject of the email?')
    subject = recognize_speech()
    
    speak('What is the body of the email?')
    body = recognize_speech()
    
    message = f"Subject: {subject}\n\n{body}"
    
    try:
        server.sendmail(username, recipient, message)
        speak("Email sent successfully!")
        print("Email sent successfully!")
    except Exception as e:
        speak("Failed to send the email.")
        print(f"Failed to send email: {e}")
        
# Function to read an email
def read_emails(username, password):
    try:
        # Connect to the Gmail IMAP server
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        imap.login(username, password)
        imap.select("inbox")

        # Search for unread emails
        status, messages = imap.search(None, 'UNSEEN')
        email_ids = messages[0].split()

        if not email_ids:
            speak("You have no unread emails.")
            print("No unread emails.")
            return

        speak(f"You have {len(email_ids)} unread email(s).")
        
        for i, email_id in enumerate(email_ids[:5], start=1):  # Limit to 5 emails
            status, msg_data = imap.fetch(email_id, '(RFC822)')
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    from_ = msg.get("From")

                    # Get email body (only text/plain)
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain" and not part.get("Content-Disposition"):
                                body = part.get_payload(decode=True).decode()
                                break
                    else:
                        body = msg.get_payload(decode=True).decode()

                    snippet = body[:100].replace("\n", " ").strip()  # First 100 characters

                    print(f"\nEmail {i}:\nFrom: {from_}\nSubject: {subject}\nBody Preview: {snippet}\n")
                    speak(f"Email {i} from {from_}. Subject: {subject}. Here's a brief preview: {snippet}")
        imap.logout()

    except Exception as e:
        print(f"Failed to read emails: {e}")
        speak("Failed to read your emails.")


# Main function to handle the interaction
def main():
    username = "anushreegupta512@gmail.com"  # Replace with your email
    password = "wpgd rzck mrrk puob"  # Replace with your app-specific password

    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(username, password)
        print('Login successful!')
        speak("Login successful!")

        while True:
            speak('What would you like to do? Say "compose", "read", or "logout".')
            command = recognize_speech()

            if 'compose' in command or 'write' in command:
                send_email(server, username)
            elif 'read' in command:
                read_emails(username, password)
            elif 'logout' in command:
                speak("Logging out.")
                print("Logging out.")
                break
            else:
                speak("Sorry, I did not understand that. Please try again.")
                print("Sorry, I did not understand that. Please try again.")
        
        server.quit()

    except Exception as e:
        print(f"Login failed: {e}")
        speak("Login failed.")

if __name__ == "__main__":
    main()
