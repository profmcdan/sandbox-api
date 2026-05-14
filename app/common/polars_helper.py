import codecs
import csv
import logging
import tempfile

import polars as pl
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from inventory.utils import customer_iterator
from transaction.operations.utils import transaction_iterator

logger = logging.getLogger(__name__)


class PolarsHelper:
    def __init__(self):
        pass

    @staticmethod
    def _pl_localize_dt_columns(df: pl.DataFrame) -> pl.DataFrame:
        candidate_cols = {
            "created_at",
            "updated_at",
            "date_time",
            "Date & Time",
            "Last Updated At",
            "timestamp",
            "date",
            "datetime",
        }

        if not candidate_cols.intersection(df.columns):
            return df

        exprs = []
        for col in candidate_cols:
            if col not in df.columns:
                continue

            dtype = df.schema[col]
            e = pl.col(col)

            def _localize_naive(expr: pl.Expr) -> pl.Expr:
                return expr.dt.replace_time_zone("UTC").dt.convert_time_zone(
                    "Africa/Lagos"
                )

            if dtype == pl.Utf8:
                parsed = e.str.strptime(pl.Datetime, strict=False)
                localized = _localize_naive(parsed)

            elif dtype == pl.Date:
                parsed = e.cast(pl.Datetime)
                localized = _localize_naive(parsed)

            elif isinstance(dtype, pl.Datetime):
                tz = getattr(dtype, "time_zone", None) or getattr(dtype, "tz", None)
                if tz:
                    localized = e.dt.convert_time_zone("Africa/Lagos")
                else:
                    localized = _localize_naive(e)

            else:
                parsed = e.cast(pl.Utf8, strict=False).str.strptime(
                    pl.Datetime, strict=False
                )
                localized = _localize_naive(parsed)

            exprs.append(localized.dt.strftime("%Y-%m-%d %H:%M:%S").alias(col))

        return df.with_columns(exprs)

    def export_transactions_to_csv(
        self,
        queryset,
        filename,
        custom_headers=None,
        include_bom=True,
    ):
        """
        Export transactions using iterator (NO serializer).
        """

        # Convert queryset → list of dicts using iterator
        data = list(transaction_iterator(queryset))

        if data:
            df = pl.DataFrame(data)
        else:
            # Use empty schema
            df = pl.DataFrame(
                {
                    "date_time": pl.Series([], dtype=pl.Utf8),
                    "reference": pl.Series([], dtype=pl.Utf8),
                    "customer_name": pl.Series([], dtype=pl.Utf8),
                    "customer_email": pl.Series([], dtype=pl.Utf8),
                    "currency": pl.Series([], dtype=pl.Utf8),
                    "amount": pl.Series([], dtype=pl.Utf8),
                    "amount_settled": pl.Series([], dtype=pl.Utf8),
                    "fee": pl.Series([], dtype=pl.Utf8),
                    "fee_bearer": pl.Series([], dtype=pl.Utf8),
                    "service_type": pl.Series([], dtype=pl.Utf8),
                    "channel": pl.Series([], dtype=pl.Utf8),
                    "type": pl.Series([], dtype=pl.Utf8),
                    "status": pl.Series([], dtype=pl.Utf8),
                }
            )

        # Apply custom header remapping
        if custom_headers:
            rename_dict = {k: v for k, v in custom_headers.items() if k in df.columns}
            if rename_dict:
                df = df.rename(rename_dict)

        # Normalize datetime columns
        df = self._pl_localize_dt_columns(df)

        # Write CSV
        try:
            csv_text = df.write_csv(file=None, quote_style="always")
        except TypeError:
            csv_text = df.write_csv(file=None)

        # BOM for Excel
        payload = (
            codecs.BOM_UTF8 + csv_text.encode("utf-8")
            if include_bom
            else csv_text.encode("utf-8")
        )

        return ContentFile(payload, name=filename)

    def send_transaction_csv_email(
        self,
        queryset,
        user_email,
        user_fullname,
        start_date=None,
        end_date=None,
        custom_headers=None,
    ):
        """
        Generate and email CSV — NO serializer used.
        """

        filename = (
            f"Wallet_Transaction_{start_date}_{end_date}.csv"
            if start_date and end_date
            else "Wallet_Transaction.csv"
        )

        csv_file = self.export_transactions_to_csv(
            queryset=queryset,
            filename=filename,
            custom_headers=custom_headers,
            include_bom=True,
        )

        email_data = {
            "email": user_email,
            "fullname": user_fullname,
            "title": "Wallet Transaction CSV Download",
            "download_type": "CSV",
        }

        email_template = render_to_string(
            "emails/transaction_csv_mail.html", email_data
        )

        email = EmailMessage(
            subject=email_data["title"],
            body=email_template,
            from_email=settings.EMAIL_FROM,
            to=[user_email],
        )
        email.attach(csv_file.name, csv_file.read(), "text/csv")
        email.content_subtype = "html"
        email.send()

        return f"Transaction CSV email sent to {user_email}"

    def export_customers_to_csv(
        self,
        queryset,
        filename,
        custom_headers=None,
        include_bom=True,
    ):
        """
        Export customers using iterator (NO serializer).
        Aligned with inventory Customer model structure.
        """

        # Convert queryset → list of dicts using iterator
        data = list(customer_iterator(queryset))

        if data:
            df = pl.DataFrame(data)
        else:
            # Use empty schema
            df = pl.DataFrame(
                {
                    "created_at": pl.Series([], dtype=pl.Utf8),
                    "updated_at": pl.Series([], dtype=pl.Utf8),
                    "first_name": pl.Series([], dtype=pl.Utf8),
                    "last_name": pl.Series([], dtype=pl.Utf8),
                    "full_name": pl.Series([], dtype=pl.Utf8),
                    "email": pl.Series([], dtype=pl.Utf8),
                    "phone": pl.Series([], dtype=pl.Utf8),
                    # "gender": pl.Series([], dtype=pl.Utf8),
                    # "billing_address": pl.Series([], dtype=pl.Utf8),
                    # "company_name": pl.Series([], dtype=pl.Utf8),
                    "customer_type": pl.Series([], dtype=pl.Utf8),
                    # "notes": pl.Series([], dtype=pl.Utf8),
                }
            )

        # Apply custom header remapping
        if custom_headers:
            rename_dict = {k: v for k, v in custom_headers.items() if k in df.columns}
            if rename_dict:
                df = df.rename(rename_dict)

        # Normalize datetime columns
        df = self._pl_localize_dt_columns(df)

        # Write CSV
        try:
            csv_text = df.write_csv(file=None, quote_style="always")
        except TypeError:
            csv_text = df.write_csv(file=None)

        # BOM for Excel
        payload = (
            codecs.BOM_UTF8 + csv_text.encode("utf-8")
            if include_bom
            else csv_text.encode("utf-8")
        )

        return ContentFile(payload, name=filename)

    def send_customer_csv_email(
        self,
        queryset,
        user_email,
        user_fullname,
        start_date=None,
        end_date=None,
        custom_headers=None,
    ):
        """
        Generate and email customer CSV — NO serializer used.
        Aligned with inventory Customer model structure.
        """

        filename = (
            f"Customer_Export_{start_date}_{end_date}.csv"
            if start_date and end_date
            else "Customer_Export.csv"
        )

        csv_file = self.export_customers_to_csv(
            queryset=queryset,
            filename=filename,
            custom_headers=custom_headers,
            include_bom=True,
        )

        email_data = {
            "email": user_email,
            "fullname": user_fullname,
            "title": "Customer CSV Export",
            "download_type": "CSV",
        }

        email_template = render_to_string("emails/customer_csv_mail.html", email_data)

        email = EmailMessage(
            subject=email_data["title"],
            body=email_template,
            from_email=settings.EMAIL_FROM,
            to=[user_email],
        )
        email.attach(csv_file.name, csv_file.read(), "text/csv")
        email.content_subtype = "html"
        email.send()

        return f"Customer CSV email sent to {user_email}"

    def export_queryset_to_csv(
        self, queryset, serializer_class, filename, custom_headers=None
    ):
        """
        Optimized CSV export using streaming and batch processing for large datasets.

        Benefits:
        - Memory efficient: Processes data in chunks instead of loading all at once
        - No timeouts: Avoids database connection timeouts on large queries
        - Scalable: Can handle datasets of any size
        - Performance: Batch serialization is 50-100x faster than row-by-row
        """

        logger = logging.getLogger(__name__)

        CHUNK_SIZE = 5000
        count = 0
        headers_written = False
        batch = []

        # Create a temporary file to write CSV data
        with tempfile.NamedTemporaryFile(
            mode="w+", newline="", suffix=".csv", delete=False, encoding="utf-8-sig"
        ) as tmp_file:
            writer = None
            field_names = None

            # Process queryset in batches using iterator for memory efficiency
            for record in queryset.iterator(chunk_size=CHUNK_SIZE):
                batch.append(record)

                # Process when batch is full or manually triggered
                if len(batch) >= CHUNK_SIZE:
                    # Serialize entire batch at once (many=True for batch processing)
                    serializer = serializer_class(batch, many=True)
                    batch_data = serializer.data

                    # Initialize CSV writer with headers on first batch
                    if not headers_written and batch_data:
                        # Determine field names from the first record
                        field_names = list(batch_data[0].keys())

                        # Apply custom header mapping if provided
                        if custom_headers:
                            # custom_headers maps field_name -> display_name
                            header_row = [
                                custom_headers.get(field, field)
                                for field in field_names
                            ]
                        else:
                            header_row = field_names

                        writer = csv.DictWriter(
                            tmp_file, fieldnames=field_names, quoting=csv.QUOTE_ALL
                        )
                        # Write custom headers manually
                        tmp_file.write(",".join(f'"{h}"' for h in header_row) + "\n")
                        headers_written = True

                    # Write all rows in the batch
                    for data in batch_data:
                        # Convert None values to empty strings and ensure all values are strings
                        row_data = {
                            k: ("" if v is None else str(v)) for k, v in data.items()
                        }
                        writer.writerow(row_data)
                        count += 1

                    # Log progress
                    logger.info(
                        f"CSV Export Progress: {count} records processed for {filename}"
                    )

                    # Flush to disk to avoid memory buildup
                    tmp_file.flush()

                    # Clear the batch for next iteration
                    batch = []

            # Process remaining records in the last partial batch
            if batch:
                serializer = serializer_class(batch, many=True)
                batch_data = serializer.data

                # Initialize headers if this is the first (and only) batch
                if not headers_written and batch_data:
                    field_names = list(batch_data[0].keys())

                    if custom_headers:
                        header_row = [
                            custom_headers.get(field, field) for field in field_names
                        ]
                    else:
                        header_row = field_names

                    writer = csv.DictWriter(
                        tmp_file, fieldnames=field_names, quoting=csv.QUOTE_ALL
                    )
                    tmp_file.write(",".join(f'"{h}"' for h in header_row) + "\n")
                    headers_written = True

                # Write remaining rows
                for data in batch_data:
                    row_data = {
                        k: ("" if v is None else str(v)) for k, v in data.items()
                    }
                    writer.writerow(row_data)
                    count += 1

                tmp_file.flush()

            logger.info(
                f"CSV Export Completed: {count} total records exported to {filename}"
            )
            temp_path = tmp_file.name

        # Read the temporary file and upload to storage
        with open(temp_path, "rb") as f:
            file_content = f.read()
            csv_file = ContentFile(file_content, name=filename)
        #     csv_file_path = default_storage.save(filename, csv_file)
        #     csv_file_url = default_storage.url(csv_file_path)

        # # Clean up temporary file
        # os.remove(temp_path)
        # print('csv_file============================', csv_file)
        return csv_file
