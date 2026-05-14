import logging
import mimetypes
from io import BytesIO

from django.conf import settings
from django.core import mail
from django.template.loader import get_template
from transaction.utils import send_email

logger = logging.getLogger(__name__)


class EmailClient:
    def send_statement_email(
        self, email_metadata, file_stream: BytesIO = None, file_extension=None
    ):
        """
        Sends email with file attachment (automatically detects MIME type).
        """
        html_email = get_template("emails/transaction_csv_mail.html").render(
            email_metadata
        )
        email = mail.EmailMessage(
            subject=email_metadata.get("title", "Wrong Transfer"),
            body=html_email,
            from_email=settings.EMAIL_FROM,
            to=[email_metadata["email"]],
        )

        if file_stream and file_extension:
            filename = f"{email_metadata.get('title', 'statement')}.{file_extension}"
            file_stream.seek(0)

            mime_type, _ = mimetypes.guess_type(filename)
            if mime_type is None:
                mime_type = "application/octet-stream"  # Fallback

            email.attach(filename, file_stream.read(), mime_type)

        email.content_subtype = "html"
        email.send()

    def send_notification(
        self,
        email_data,
        html_template_file,
        text_template_file,
        attachment_name="transaction_receipt",
        should_attach_pdf=False,
    ):
        html_template = get_template(html_template_file)
        text_template = get_template(text_template_file)
        html_alternative = html_template.render(email_data)
        text_alternative = text_template.render(email_data)
        send_email(
            email_data["title"] or "Transaction Successful",
            email_data["email"],
            html_alternative,
            text_alternative,
            attachment_name,
            should_attach_pdf,
        )
