import os
from datetime import datetime
from pathlib import Path

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr

# Settings for FastMail using Env Vars or Defaults for local dev
conf = ConnectionConfig(
    MAIL_USERNAME=os.environ.get("MAIL_USERNAME", "dev@wakala.ma"),
    MAIL_PASSWORD=os.environ.get("MAIL_PASSWORD", "secret"),
    MAIL_FROM=os.environ.get("MAIL_FROM", "noreply@wakala.ma"),
    MAIL_PORT=int(os.environ.get("MAIL_PORT", 1025)),
    MAIL_SERVER=os.environ.get("MAIL_SERVER", "localhost"),
    MAIL_STARTTLS=os.environ.get("MAIL_STARTTLS", "False").lower() in ("true", "1", "t"),
    MAIL_SSL_TLS=os.environ.get("MAIL_SSL_TLS", "False").lower() in ("true", "1", "t"),
    USE_CREDENTIALS=os.environ.get("USE_CREDENTIALS", "False").lower() in ("true", "1", "t"),
    VALIDATE_CERTS=os.environ.get("VALIDATE_CERTS", "False").lower() in ("true", "1", "t"),
)


async def send_otp_email(email: str, otp_code: str):
    """
    Envoie un email HTML contenant le code OTP.
    """
    html_content = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Inter', Arial, sans-serif;
                background-color: #F8F7F4;
                color: #122135;
                margin: 0;
                padding: 40px;
                text-align: center;
            }}
            .container {{
                background-color: #FFFFFF;
                max-width: 500px;
                margin: 0 auto;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 4px 16px rgba(18, 33, 53, 0.08);
            }}
            .logo {{
                font-family: 'Cormorant Garamond', serif;
                font-size: 2rem;
                color: #122135;
                margin-bottom: 24px;
            }}
            h1 {{
                font-size: 1.5rem;
                margin-bottom: 16px;
            }}
            p {{
                font-size: 1rem;
                color: #4A5568;
                line-height: 1.5;
            }}
            .otp-box {{
                background-color: #F1EFE9;
                border: 1px solid #AE8C4E;
                color: #122135;
                font-size: 2.5rem;
                font-weight: 700;
                letter-spacing: 0.2em;
                padding: 16px 24px;
                border-radius: 8px;
                display: inline-block;
                margin: 24px 0;
            }}
            .footer {{
                margin-top: 32px;
                font-size: 0.85rem;
                color: #8492A6;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">WAKALA</div>
            <h1>Vérification de votre adresse e-mail</h1>
            <p>Bienvenue sur Wakala ! Veuillez utiliser le code de vérification suivant pour finaliser la création de votre compte.</p>
            
            <div class="otp-box">{otp_code}</div>
            
            <p>Ce code expire dans 10 minutes. Si vous n'avez pas demandé ce code, vous pouvez ignorer cet e-mail.</p>
            
            <div class="footer">
                &copy; {datetime.now().year} Wakala. Tous droits réservés.
            </div>
        </div>
    </body>
    </html>
    """

    message = MessageSchema(
        subject="Votre code de vérification Wakala",
        recipients=[email],
        body=html_content,
        subtype=MessageType.html,
    )

    fm = FastMail(conf)
    try:
        await fm.send_message(message)
    except Exception as e:
        print(f"Error sending email to {email}: {e}")
