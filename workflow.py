from system_instructions import MAIN_WRITER_SYSTEM_INSTRUCTIONS, LINK_INJECTER_SYSTEM_INSTRUCTIONS, PHILOSOPHER_SYSTEM_INSTRUCTIONS, EDITOR_SYSTEM_INSTRUCTIONS
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
main_writer_links = []
for step in main_writer.steps:
    if step.type == "model_output":
        for content_block in step.content:
            if content_block.type == "text":
                if content_block.annotations:
                    for annotation in content_block.annotations:
                        if annotation.type == "url_citation":
                            cited_text = content_block.text[annotation.start_index:annotation.end_index]
                            main_writer_links.append({'url':annotation.url,'text':cited_text})

# 2. Link injecter injects links
link_injecter = client.interactions.create(
    model="gemini-3.5-flash",
    input=f'''
        MAIN WRITER DRAFT:
        {main_writer_output}

        REFERENCES:
        {main_writer_links}
    ''',
    system_instruction=LINK_INJECTER_SYSTEM_INSTRUCTIONS,
)
link_injecter_output = link_injecter.output_text
with open('output_2.md', 'w', encoding="utf-8") as f:
    f.write(link_injecter_output)

# 3. Philosopher agent makes a structured reflection on freedom
philosopher = client.interactions.create(
    model="gemini-3.1-pro-preview",
    input=link_injecter_output,
    system_instruction=PHILOSOPHER_SYSTEM_INSTRUCTIONS
)
philosopher_output = philosopher.output_text

# 4. Editor agent edits the outputs of the fact checker and philospher

editor_1 = client.interactions.create(
    model="gemini-3.5-flash",
    input=link_injecter_output,
    system_instruction=EDITOR_SYSTEM_INSTRUCTIONS
)
editor_output_news = editor_1.output_text

editor_2 = client.interactions.create(
    model="gemini-3.5-flash",
    input=philosopher_output,
    system_instruction=EDITOR_SYSTEM_INSTRUCTIONS
)
editor_output_reflections = editor_2.output_text

final_output = f'''
**NIKA NEWSLETTER - WEEK OF {today_minus_seven} TO {today}**

Welcome to the Nika newsletter, focusing on the recent developments on freedom around the world.

# WHAT'S NEW

{editor_output_news}

# WHAT WE THINK

{editor_output_reflections}

Stay free out there,

Fede & Nika

*The above newsletter is AI-generated. However, the [underlying multi-agent
system](https://federicobindi.com/projects/nika-newsletter) employs a robust 
system of cross-checks.*
'''
with open('output_4.md', 'w', encoding="utf-8") as f:
    f.write(final_output)

# 5. Saving output to MongoDB
strucured_output = {
    'ts':ts,
    'text_text':final_output
}

# 6. Emailing output to subscribers and sharing in LinkedIn