from io import BytesIO

import pdfkit
from django.conf import settings
from django.template.loader import render_to_string
from pypdf import PdfReader, PdfWriter


class PdfGenerator:
    def __init__(self):
        self.pdf_config = pdfkit.configuration(
            wkhtmltopdf=settings.WKHTMLTOPDF_BINARY_PATH
        )
        self.pdf_options = {
            "page-size": "A4",
            "encoding": "UTF-8",
            "quiet": "",
            "enable-local-file-access": None,
        }

    def _assemble_pdf_bytes(self, raw_pdf_bytes: bytes) -> BytesIO:
        """
        Wrap pdf bytes into a BytesIO and validate re-write with pypdf to ensure structure.
        """
        pdf_io = BytesIO(raw_pdf_bytes)
        try:
            reader = PdfReader(pdf_io)
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            out = BytesIO()
            writer.write(out)
            out.seek(0)
            return out
        except Exception:
            pdf_io.seek(0)
            return pdf_io

    def _generate_single_pdf(self, html_content: str) -> BytesIO:
        try:
            raw_pdf = pdfkit.from_string(
                html_content,
                False,
                configuration=self.pdf_config,
                options=self.pdf_options,
            )
            return self._assemble_pdf_bytes(raw_pdf)
        except Exception as e:
            print(str(e))
            raise RuntimeError(f"PDF generation failed: {str(e)}")

    def download_pdf(
        self, data=None, template: str = None, model: str = None, title: str = None
    ):
        html = render_to_string(
            template,
            {
                model: data,
                "title": title,
            },
        )

        pdf_stream = self._generate_single_pdf(html)
        pdf_stream.seek(0)
        return pdf_stream
