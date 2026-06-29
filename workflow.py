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
    input="Execute your system instructions.",
    system_instruction=MAIN_WRITER_SYSTEM_INSTRUCTIONS,
    tools=[{"type": "google_search"}]
)
main_writer_output = main_writer.output_text
with open('output_1.txt', 'w') as f:
    f.write(main_writer_output)

# 2. Fact checker agent revises draft
fact_checker = client.interactions.create(
    model="gemini-2.5-flash",
    input=f"Execute your system instructions. Main writer output: {main_writer_output}",
    system_instruction=FACT_CHECKER_SYSTEM_INSTRUCTIONS,
    tools=[{"type": "google_search"}]
)
fact_checker_output = main_writer.output_text
with open('output_2.txt', 'w') as f:
    f.write(fact_checker_output)

# 3. Philosopher agent makes a structured reflection on freedom
philosopher = client.interactions.create(
    model="gemini-2.5-flash",
    input=f"Execute your system instructions. Fact checker output: {fact_checker_output}",
    system_instruction=PHILOSOPHER_SYSTEM_INSTRUCTIONS
)
philosopher_output = main_writer.output_text
with open('output_3.txt', 'w') as f:
    f.write(philosopher_output)