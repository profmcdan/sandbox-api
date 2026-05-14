from django.conf import settings
from opensearchpy import OpenSearch

# OpenSearch client
opensearch_client = OpenSearch(
    hosts=[{"host": settings.OPENSEARCH_HOST, "port": settings.OPENSEARCH_PORT}],
    http_auth=(
        settings.OPENSEARCH_USERNAME,
        settings.OPENSEARCH_PASSWORD,
    ),
    use_ssl=settings.OPENSEARCH_USE_SSL,
    verify_certs=False,
    http_compress=True,
)

INDEX_NAME = settings.APP_NAME.lower().strip().replace(" ", "")

