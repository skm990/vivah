from django.core.mail import get_connection, send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string



def send_interest_email(receiver_profile, sender_user, sender_profile):
    subject = f"{sender_user.first_name} has shown interest in your Vivah profile"
    from_email = "noreply@example.com"
    to = [receiver_profile.user.email]

    html_content = render_to_string(
        'interest_email_template.html',
        {
            'receiver_name': receiver_profile.user.first_name,
            'sender_name': sender_user.first_name,
            'login_url': " https://6bcff533543f.ngrok-free.app",  # replace with live URL
        }
    )
    text_content = (
        f"Hi {receiver_profile.user.first_name},\n\n"
        f"{sender_user.first_name} has expressed interest in your profile on Vivah.\n"
        f"Please log in to your account to view their profile and respond accordingly.\n\n"
        f"Best regards,\n"
        f"Vivah Team"
    )

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def send_interest_accept_email(receiver_profile, email, sender_first_name):
    """
    Send an email notification when a user's interest is accepted.
    receiver_profile: the profile of the person whose interest was accepted
    sender_user: the user who accepted the interest
    """
    subject = f"{receiver_profile.user.first_name} has accepted your interest request on Vivah"
    from_email = "noreply@example.com"
    to = [email]

    html_content = render_to_string(
        'interest_accept_email_template.html',  # you can use a new template for acceptance
        {
            'receiver_name': receiver_profile.user.first_name,
            'sender_name': sender_first_name,
            'login_url': " https://6bcff533543f.ngrok-free.app",  # replace with live URL
        }
    )
    text_content = (
        f"Hi {receiver_profile.user.first_name},\n\n"
        f"Good news! {sender_first_name} has accepted your interest request on Vivah.\n"
        f"You can log in to your account to view their profile and continue your conversation.\n\n"
        f"Best wishes,\n"
        f"Vivah Team"
    )

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def send_otp_email(email, otp, user_name="User"):
    subject = "OTP for Vivah Login"
    from_email = "noreply@example.com"
    to = [email]

    html_content = render_to_string('auth/otp_email_template.html', {'otp': otp, 'user_name': user_name})
    text_content = f"Hello {user_name},\nYour Login OTP for Vivah is {otp}. Valid for 10 minutes."

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()

