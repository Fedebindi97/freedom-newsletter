from system_instructions import MAIN_WRITER_SYSTEM_INSTRUCTIONS
from dotenv import load_dotenv
import os
from google import genai
from system_instructions import *

# 0. Load env vars and initialize Gemini client
load_dotenv()
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
client = genai.Client(api_key=GEMINI_API_KEY)

# 1. Main writer agent creates first draft
main_writer = client.interactions.create(
    model="gemini-2.5-flash",
    input="What day is it today?"
)
main_writer_output = main_writer.output_text
print(main_writer_output)
