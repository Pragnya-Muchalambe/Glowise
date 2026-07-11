import os
from dotenv import load_dotenv

load_dotenv()


class Config:

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "glowise-secret-key"
    )

    GEMINI_API_KEY = os.getenv(
        "GEMINI_API_KEY"
    )

    OPENWEATHER_API_KEY = os.getenv(
        "OPENWEATHER_API_KEY"
    )

    UPLOAD_FOLDER = "uploads"

    MAX_CONTENT_LENGTH = 10 * 1024 * 1024

    ALLOWED_EXTENSIONS = {

        "png",

        "jpg",

        "jpeg",

        "webp"

    }

    DATABASE = "glowise.db"


def allowed_file(filename):

    return (

        "." in filename

        and

        filename.rsplit(".",1)[1].lower()

        in

        Config.ALLOWED_EXTENSIONS

    )