import os
from litellm import completion
from openai import APIConnectionError, OpenAIError, RateLimitError
from dotenv import load_dotenv
from pathlib import Path

# load parameters from .env
dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)

# Get OPENAI Setting
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI__MODEL = os.getenv('OPENAI_MODEL')

try:
    response = completion(
        #model=OPENAI__MODEL,
        model="ollama/openchat",
        messages = [
                {"role": "system", "content": "You are a helpful system assistant. Here is the system information: "},
                {"role": "system", "content": '''
                - Module Name: Import Letter of Credit
                    Module ID: IPLC
                    Module Description: >-
                    Import Letter of Credit (LC) is a financial instrument issued by a bank on
                    behalf of an importer, guaranteeing payment to the exporter once the
                    required documents are presented and all conditions stated in the LC are
                    met. It acts as a payment assurance for the exporter, ensuring that they
                    will be paid for the goods or services provided to the importer. The bank
                    that issues the LC takes responsibility for the payment, providing
                    confidence to both the importer and exporter in the transaction.
                    -  Functions:
                        - Function Name: Register Letter of Credit
                            Function ID: F05030702010
                            Description: >-
                            In this function, the incoming import LC is recorded and documented in
                            the trade finance system of the bank. It involves capturing key
                            information such as LC number, issuing bank details, applicant and
                            beneficiary information, LC amount, and terms and conditions.
                            - KeyFields:
                                - Key Field: EXPIRY_PLC
                                    Filed Value(enumeration): 'BENEFICIARY COUNTRY,AT OUR COUNTERS,ADVISING BANK COUNTRY,OTHER'
                                    Description: This refers to the place where the LC expires.
                                - Key Field: FORM_OF_LC
                                    Field Type: SELECT
                                    Filed Value(enumeration): 'IRREVOCABLE, IRREVOCABLE TRANSFERABLE'
                                    Description: This indicates the type of LC.
                                - Key Field: EXPIRY_DT
                                    Field Type: DATE
                                    Description: This refers to the date on which the LC expires.
                                - Key Field: LC_CCY
                                    Field Type: CCY
                                    Filed Value(enumeration): ISO4217
                                    Description: Use the fields provided to specify the currency of the LC.
                                - Key Field: LC_AMT
                                    Field Type: AMOUNT
                                    Description: Use the fields provided to specify the amount of the LC.
                                - Key Field: APPLICANT
                                    Field Type: CUSTOMER
                                    Description: This refers to the Id of the Applicant.
                                - Key Field: ADVISE_BANK
                                    Field Type: BANK
                                    Description: This refers to the Id of the Advising Bank.
                                - Key Field: AVAL_BY
                                    Field Type: SELECT
                                    Filed Value(enumeration): "BY PAYMENT, BY ACCEPTANCE, BY NEGOTIATION, BY DEF PAYMENT, BY MIXED PYMT"
                                    Description: This indicates the method by which the LC is available.
                        - Function Name: Issue Letter of Credit
                            Function ID: F05030702015
                            Description: >-
                                This function involves the issuance of the import LC by the bank on
                                behalf of the importer. The bank prepares the LC document, including the
                                terms and conditions, and sends it to the beneficiary (exporter) or
                                their bank.
                            - KeyFields:
                                - Key Field: FORM_OF_LC
                                    Field Type: SELECT
                                    Filed Value(enumeration): 'IRREVOCABLE, IRREVOCABLE TRANSFERABLE'
                                    Description: Form of Documentary Credit
                                - Key Field: EXPIRY_PLC
                                    Field Type: SELECT
                                    Filed Value(enumeration): 'BENEFICIARY COUNTRY,AT OUR COUNTERS,ADVISING BANK COUNTRY,OTHER'
                                    Description: Expiry Place
                                - Key Field: APLB_RULE
                                    Field Type: SELECT
                                    Filed Value(enumeration): >-
                                        EUCP LATEST VERSION,EUCP LATEST VERSION,EUCPURR LATEST VERSION,OTHER,UCP LATEST
                                        VERSION,UCPURR LATEST VERSION
                                    Description: Applicable Rules
                                - Key Field: AVAL_BY
                                    Field Type: SELECT
                                    Filed Value(enumeration): "BY PAYMENT, BY ACCEPTANCE, BY NEGOTIATION, BY DEF PAYMENT, BY MIXED PYMT"
                                    Description: Available By
                 '''
                },
                {"role": "user", "content": "Chinasystems Ltd. Corp. applied for a non-transferable letter of credit worth US$100,000" },
                {"role": "assistant", "content": "Which function the user to perform? Which key fields did the user gave? Leave the values blank for the fields which the user did not gave. Answer in JSON format only." }
            ],
            temperature=0,
            max_tokens=512,
            api_base="http://10.39.101.14:11434"
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
    print(response.choices[0].message)