from system_instructions import MAIN_WRITER_SYSTEM_INSTRUCTIONS, FACT_CHECKER_SYSTEM_INSTRUCTIONS, PHILOSOPHER_SYSTEM_INSTRUCTIONS, EDITOR_SYSTEM_INSTRUCTIONS
from dotenv import load_dotenv
import os
from google import genai

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
with open('output_1.md', 'w', encoding="utf-8") as f:
    f.write(main_writer_output)

# 2. Fact checker agent revises draft
fact_checker = client.interactions.create(
    model="gemini-2.5-flash",
    input=f"Execute your system instructions. Main writer output: {main_writer_output}",
    system_instruction=FACT_CHECKER_SYSTEM_INSTRUCTIONS,
    tools=[{"type": "google_search"}]
)
fact_checker_output = fact_checker.output_text
with open('output_2.md', 'w', encoding="utf-8") as f:
    f.write(fact_checker_output)

# 3. Philosopher agent makes a structured reflection on freedom
philosopher = client.interactions.create(
    model="gemini-2.5-flash",
    input=f"Execute your system instructions. Fact checker output: {fact_checker_output}",
    system_instruction=PHILOSOPHER_SYSTEM_INSTRUCTIONS
)
philosopher_output = philosopher.output_text
with open('output_3.md', 'w', encoding="utf-8") as f:
    f.write(philosopher_output)

# 4. Editor agent edits the output
content_to_edit = f'''
    {fact_checker_output}

    {philosopher_output}
'''

editor = client.interactions.create(
    model="gemini-2.5-flash",
    input=f"Execute your system instructions. Content to edit: {content_to_edit}",
    system_instruction=EDITOR_SYSTEM_INSTRUCTIONS
)
editor_output = editor.output_text
with open('output_4.md', 'w', encoding="utf-8") as f:
    f.write(editor_output)

final_output = f'''
    {editor_output}

    * The above newsletter is AI-generated. However, the underlying multi-agent
    system employs a robust system of cross-checks. *
'''

# 5. Saving output to MongoDB

# 6. Emailing output to subscribers and sharing in LinkedIn