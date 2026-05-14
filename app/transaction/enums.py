TRANSACTION_STATUS_CHOICES = (
    ('pending', 'pending'),
    ('successful', 'successful'),
    ('failed', 'failed'),
)

TRANSACTION_MODE_CHOICES = (
    ('credit', 'credit'),
    ('debit', 'debit'),
)

TRANSACTION_CLASS_CHOICES = (
    ('transfer', 'transfer'),
    ('vas', 'vas'),
    ('cashout', 'cashout'),
    ('inward', 'inward'),
)