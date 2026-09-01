"""
Placeholder email delivery.

For local development / this stage of the project, "sending" an email
just means printing it clearly to the backend console so the reset flow
is fully testable end-to-end without needing real SMTP credentials.

To go to production: replace the body of send_password_reset_email()
with a call to a real provider (e.g. SendGrid, Postmark, SES) — nothing
else in the app needs to change, since every caller only depends on
this function's signature, not its implementation.
"""


def send_password_reset_email(to_email: str, reset_link: str) -> None:
    print("=" * 60)
    print("PASSWORD RESET EMAIL (console stub — no real email sent)")
    print(f"To: {to_email}")
    print(f"Reset link: {reset_link}")
    print("This link expires in 30 minutes.")
    print("=" * 60)