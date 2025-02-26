from google.cloud import firestore
import os

# Ensure the environment variable is set
if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
    raise EnvironmentError("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set")

db = firestore.Client()