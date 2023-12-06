import logging
import json
from litellm import completion
from openai import APIConnectionError, OpenAIError, RateLimitError
from mako.template import Template

global OPENAI_API_KEY, OPENAI_MODEL, PROMPTS_PATH

def identify_function(userCommand, functionList):
    logging.info("Generate prompts")
    prompt_template = PROMPTS_PATH + "/function.txt"
    template = Template(filename=prompt_template, module_directory='/tmp/mako_modules')
    prompt = template.render(functions=functionList, command=userCommand)
    #prompt_messages = json.loads(prompt)

    logging.info("Calling llm API")
    try:
        response = completion(
            model=OPENAI_MODEL,
            #model="ollama/openchat",
            messages = [prompt],
            temperature=0,
            max_tokens=512
            #api_base="http://localhost:11434"
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
        return response.choices[0].message