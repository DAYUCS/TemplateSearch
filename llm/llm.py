import logging
import multiline
from litellm import completion
from openai import APIConnectionError, OpenAIError, RateLimitError
from mako.template import Template

global OPENAI_API_KEY, OPENAI_MODEL, PROMPTS_PATH

def identify_function(userCommand, functionList):
    logging.info("Generate prompts")
    prompt_template = PROMPTS_PATH + "/function.txt"
    template = Template(filename=prompt_template, module_directory='/tmp/mako_modules')
    prompt = template.render(functions=functionList, command=userCommand)
    logging.info(prompt)
    prompt_messages = multiline.loads(prompt, multiline=True)
    logging.info(prompt_messages)

    logging.info("Calling llm API")
    try:
        response = completion(
            model=OPENAI_MODEL,
            #model="ollama/openchat",
            messages = prompt_messages,
            temperature=0,
            max_tokens=512
            #api_base="http://localhost:11434"
        )
        logging.info(response)
        response_json = multiline.loads(response.choices[0].message.content.lstrip('```json').rstrip('```'))
        return response_json
    except OpenAIError as e:
        #Handle API error here, e.g. retry or log
        logging.error(e)
        return {'code': e.status_code, 'reason': e.message}