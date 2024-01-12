import base64
import os
import multiline
from litellm import completion
from openai import APIConnectionError, OpenAIError, RateLimitError
from dotenv import load_dotenv
from pathlib import Path

# load parameters from .env
dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)

# Get OPENAI Setting
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = "gpt-4-vision-preview"

# function of encoding image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Get image and encode
image_path = "/home/dayu/projects/TemplateSearch/learn_qdrant/Template1_Instance0.jpg"
base64_image = encode_image(image_path)

try:
    response = completion(
        model=OPENAI_MODEL,
        messages = [
                {"role": "user", 
                 "content":
                 [
                    {
                        "type": "text",
                        "text": "Here is an image of invoice. Please give details of the invoice in a JSON format."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
                }
            ],
            temperature=0,
            max_tokens=1024
    )
except OpenAIError as e:
    #Handle API error here, e.g. retry or log
    print(f"OpenAI API returned an API Error: {e}")
    pass
except APIConnectionError as e:
    #Handle connection error here
    print(f"Failed to connect to OpenAI API: {e}")
    pass
except RateLimitError as e:
    #Handle rate limit error (we recommend using exponential backoff)
    print(f"OpenAI API request exceeded rate limit: {e}")
    pass
else:
    response_json = multiline.loads(response.choices[0].message.content.lstrip('```json').rstrip('```'))
    print(response_json)