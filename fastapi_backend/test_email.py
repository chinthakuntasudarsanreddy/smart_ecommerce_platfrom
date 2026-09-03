import asyncio

from app.utils.email import send_email


async def main():
    await send_email(
        recipient="chinthakuntasudarsanreddy@gmail.com",
        subject="Smart E-Commerce - Mailtrap Test",
        body="This is a test email from the Smart E-Commerce Platform."
    )

    print("EMAIL SENT SUCCESSFULLY")


asyncio.run(main())