from system_instructions import MAIN_WRITER_SYSTEM_INSTRUCTIONS, LINK_INJECTER_SYSTEM_INSTRUCTIONS, PHILOSOPHER_SYSTEM_INSTRUCTIONS, EDITOR_SYSTEM_INSTRUCTIONS, SUMMARIZER_SYSTEM_INSTRUCTIONS
from time_objects import today, today_minus_seven, ts
from dotenv import load_dotenv
import os
from google import genai
from pymongo import MongoClient
import markdown
from mailchimp_marketing import Client
import certifi


# 0. Load env vars and initialize Gemini, PyMongo and Mailchimp clients
#load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
conn_string = f'mongodb+srv://bindifederico_db_user:{MONGO_PASSWORD}@cluster0.nndb8ya.mongodb.net/?appName=Cluster0&compressors=zlib'
ca = certifi.where()
mongo_client = MongoClient(conn_string, tlsCAFile=ca)
database = mongo_client.get_database("nika-newsletter")
collection = database['newsletter-texts']

MAILCHIMP_API_KEY = os.getenv("MAILCHIMP_API_KEY")
MAILCHIMP_SERVER_PREFIX = os.getenv("MAILCHIMP_SERVER_PREFIX")
AUDIENCE_ID = os.getenv("MAILCHIMP_AUDIENCE_ID")
mailchimp_client = Client()
mailchimp_client.set_config({
    "api_key": MAILCHIMP_API_KEY,
    "server": MAILCHIMP_SERVER_PREFIX
})

# 0. Summarizer agent summarizes previous issues of the newsletter
previous_issues = database["newsletter-texts"].find({}, {"ts":1, "text": 1, "_id": 0}).sort("ts", -1).limit(3).to_list()
summarizer = client.interactions.create(
    model="gemini-3.5-flash",
    input=previous_issues,
    system_instruction=SUMMARIZER_SYSTEM_INSTRUCTIONS,
    tools=[{"type": "google_search"}]
)
summarizer_output = summarizer.output_text

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

# 3. Philosopher agent makes a structured reflection on freedom
philosopher = client.interactions.create(
    model="gemini-3.1-pro-preview",
    input=f'''
    CURRENT ISSUE:
    {link_injecter_output}

    SUMMARY OF PREVIOUS ISSUES:
    {summarizer_output}
    ''',
    system_instruction=PHILOSOPHER_SYSTEM_INSTRUCTIONS
)
philosopher_output = philosopher.output_text

# 4. Editor agents edit the outputs of the fact checker and philospher

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

# 5. Saving output to MongoDB
structured_output = {
    'ts':ts,
    'text':final_output
}
result = collection.insert_one(structured_output)

# 6. Emailing output to subscribers (MailChimp) 

html_body = markdown.markdown(final_output)

compiled_html = f"""
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            h1, h2, h3 {{ color: #111111; }}
            code {{ background: #f4f4f4; padding: 2px 4px; border-radius: 4px; }}
            pre {{ background: #f4f4f4; padding: 10px; border-radius: 4px; overflow-x: auto; }}
        </style>
    </head>
    <body>
        {html_body}
    </body>
</html>
"""

campaign_payload = {
    "type": "regular",
    "recipients": {"list_id": AUDIENCE_ID},
    "settings": {
        "subject_line": f"NIKA NEWSLETTER - WEEK OF {today_minus_seven} TO {today}",
        "from_name": "Nika Newsletter",
        "reply_to": "bindi.federico@gmail.com"
    }
}

campaign = mailchimp_client.campaigns.create(campaign_payload)
campaign_id = campaign["id"]
mailchimp_client.campaigns.set_content(campaign_id, {"html": compiled_html})
mailchimp_client.campaigns.send(campaign_id)