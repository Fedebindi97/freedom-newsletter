from system_instructions import MAIN_WRITER_SYSTEM_INSTRUCTIONS, FACT_CHECKER_SYSTEM_INSTRUCTIONS, PHILOSOPHER_SYSTEM_INSTRUCTIONS, EDITOR_SYSTEM_INSTRUCTIONS
from time_objects import today, today_minus_seven, ts
from dotenv import load_dotenv
import os
from google import genai

# 0. Load env vars and initialize Gemini client
load_dotenv()
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
client = genai.Client(api_key=GEMINI_API_KEY)

# 1. Main writer agent creates first draft
main_writer = client.interactions.create(
    model="gemini-3.1-pro-preview",
    input="Execute your system instructions.",
    system_instruction=MAIN_WRITER_SYSTEM_INSTRUCTIONS,
    tools=[{"type": "google_search"}]
)
main_writer_output = main_writer.output_text

print(main_writer.steps)