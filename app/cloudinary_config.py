import cloudinary
from dotenv import load_dotenv
import os

load_dotenv()

CLOUDINARY_NAME=os.getenv("CLOUDINARY_NAME")
CLOUDINARY_API_KEY=os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET=os.getenv("CLOUDINARY_API_SECRET")


cloudinary.config(

    cloud_name=CLOUDINARY_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True
)

