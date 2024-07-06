import os

import google.ai.generativelanguage as glm
from google.oauth2 import service_account


class GenerativeServiceClient:
    def __init__(self):
        credentials = service_account.Credentials.from_service_account_info(
            {
                "type": "service_account",
                "project_id": os.environ.get("project_id"),
                "private_key_id": os.environ.get("private_key_id"),
                "private_key": os.environ.get("private_key"),
                "client_email": "animan@animan-review.iam.gserviceaccount.com",
                "client_id": "100602855326530228987",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/animan%40animan-review.iam.gserviceaccount.com",
                "universe_domain": "googleapis.com",
            }
        )

        scoped_credentials = credentials.with_scopes(
            [
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/generative-language.retriever",
            ]
        )

        self.gsc = glm.GenerativeServiceClient(credentials=scoped_credentials)

    def get(self):
        return self.gsc
