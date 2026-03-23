# Vercel serverless entry point — imports the Flask app from the project root.
# Vercel adds the project root to sys.path automatically, so this just works.
from app import app  # noqa: F401  (Vercel looks for the `app` name)
