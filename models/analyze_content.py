# # uvicorn analyze_content:app --host 0.0.0.0 --port 8000 --reload

# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware

# from pydantic import BaseModel

# import openai
# import json
# import yaml

# # Load the config.yaml file
# with open("models/config.yaml", "r") as file:
#     config = yaml.safe_load(file)

# openai.api_key = config["openai_key"]

# finetuned_models = {'argument_finetuned_model': 'ft:gpt-3.5-turbo-0125:personal::B3xAsgP1', 
#                     'atomizer_finetuned_model': 'ft:gpt-3.5-turbo-0125:personal::B3yyOMLV',
#                     'critical_fine_tuned_model': 'ft:gpt-3.5-turbo-0125:personal::B3zr6iGR'}

# app = FastAPI()

# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["chrome-extension://ombijklbobodnojkjcbiohjdggnfikbc"],
# #     allow_credentials=True,
# #     allow_methods=["*"],
# #     allow_headers=["*"],
# # )
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["chrome-extension://ombijklbobodnojkjcbiohjdggnfikbc"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# class AnalyzeRequest(BaseModel):
#     paragraph: str

# def get_latest_finetuned_model(job_name):
#     """
#     Retrieves the most recent fine-tuned model for a given job.
#     """
#     fine_tuned_models = openai.FineTuningJob.list()

#     for job in fine_tuned_models["data"]:
#         if job["status"] == "succeeded" and job_name in job["fine_tuned_model"]:
#             return job["fine_tuned_model"]
    
#     return None  


# # def preprocess(para):
# #     return para[:500]
# import re

# def preprocess(para, max_length=1000):
#     """
#     Truncate the paragraph to the nearest sentence ending occurring at or after max_length.
#     """
#     if len(para) <= max_length:
#         return para  # Return full paragraph if shorter than max_length

#     # Find the nearest sentence-ending punctuation after max_length
#     match = re.search(r'[.!?]', para[max_length:])  # Look for punctuation after max_length
    
#     if match:
#         end_index = max_length + match.start() + 1  # Get index after punctuation
#         return para[:end_index].strip()
#     else:
#         return para[:max_length].strip()  # If no punctuation found, return hard cutoff

# # # Example Usage:
# # text = "Artificial intelligence is changing the world. It has impacted many industries, from healthcare to finance. The potential is limitless!"
# # print(preprocess(text))


# @app.get("/version")
# def get_version():
#     return {"version": "Unbias.me v1.1"}

# @app.post("/analyze")
# async def analyze_content(request: AnalyzeRequest):
#     """
#     This function processes the input paragraph and returns the analysis.
#     """
#     """
#     End-to-end function that:
#     1. Detects if an argument/strong stance exists.
#     2. Extracts claims and atomizes them.
#     3. Generates critical perspectives for each atomic claim.
#     Returns structured critical thoughts.
#     """
#     paragraph = preprocess(request.paragraph)

   
#     extracted_claims = paragraph.split('\n')

#     ### 🔹 Step 2: Atomize the Extracted Claims ###
#     atomized_claims = []
#     # print(f"argument model returns - {extracted_claims=}")
#     for claim in extracted_claims:
#         atomization_prompt = f"""
#         Break down the following claim into atomic facts.
#         Ensure each fact is self-contained, concise, and retains the original meaning.
#         Output should be a structured list of atomic claims.

#         Claim: {claim}
#         """
        
#         response = openai.ChatCompletion.create(
#             model=finetuned_models['atomizer_finetuned_model'],
#             messages=[{"role": "system", "content": "You are an AI that breaks down complex claims into atomic claims."},
#                       {"role": "user", "content": atomization_prompt}]
#         )
        
#         atomized_output = response["choices"][0]["message"]["content"]
#         atomized_claims.extend(atomized_output.split("\n"))  # Collecting all atomic claims

#     ### 🔹 Step 3: Generate Critical Perspectives ###
#     critical_thoughts = []

#     for atomic_claim in atomized_claims:
#         critique_prompt = f"""
#         Critically analyze the following atomic claim.
#         Provide alternative perspectives, question underlying assumptions, and explore potential biases.
#         Generate a structured critical assessment.

#         Atomic Claim: {atomic_claim}
#         """
        
#         response = openai.ChatCompletion.create(
#             model='gpt-3.5-turbo',
#             messages=[{"role": "system", "content": """Generate critical perspectives on claims given by user, challenge and expand claims by providing thought-provoking critiques. 
#                        for example, 
#                        Input: 'The one-child policy has been a major success, reducing overpopulation and improving China's economy. While controversial, most citizens support it, and studies show it has led to better healthcare for women. The government remains firm in its decision, arguing that any negative consequences are outweighed by long-term benefits.'
#                        Output: 'What are the ethical concerns about limiting family size? Is economic gain a justification for restricting personal freedoms?\n- How reliable are the studies supporting this policy? Are they government-funded, and do they account for hidden consequences like gender imbalance?\n- Are there long-term economic risks, such as an aging population and labor shortages, that counterbalance the short-term benefits?\n- The claim that 'most citizens support it'\u2014does this account for people who are afraid to speak against government policies?\n- What alternative policies could have achieved the same outcome with less human rights impact?'
#                        Similar to above critical line of thought to evaluate the presented argument, generate critical lines of thought for user given input. """},
#                       {"role": "user", "content": critique_prompt}]
#         )
        
#         critique_output = response["choices"][0]["message"]["content"]
#         critical_thoughts.append({"claim": atomic_claim, "critique": critique_output})
#     critique = '\n'.join(ct['critique'] for ct in critical_thoughts)
#     critique = critique.strip(' ').strip('-').strip('\n').strip(',')
#     return {"text": paragraph, "critique":critique}

# @app.post("/analyze")
# def analyze_paragraph(paragraph):
#     """
#     End-to-end function that:
#     1. Detects if an argument/strong stance exists.
#     2. Extracts claims and atomizes them.
#     3. Generates critical perspectives for each atomic claim.
#     Returns structured critical thoughts.
#     """
#     paragraph = preprocess(paragraph)

#     # ### 🔹 Step 1: Detect Argument in Paragraph ###
#     # argument_detection_prompt = f"""
#     # Analyze the given paragraph and determine whether it contains a strong argument, claim, or stance.
#     # If the paragraph contains an argument, extract the key claims or positions stated.
#     # Output should be either:
#     # if no arguments found in paragraph - return None
#     # else, only return the lines in the paragraph that contains the arguments. 
#     # For example,
#     # Input: 'So if you think that people get value off of art or if people get value from listening to music, if it makes our lives better it's important, make sure the you're supporting the people who give you that sense of happiness when you listen to a great song and debate we which this is supported, is by making sure they're able to make a living by doing what they're doing, but without an intellectual property right it's, impossible for them to actually make this living because anyone can just rip them off use their song'
#     # Output: 'It argues why we should not abolish intellectual property rights'"

#     # Using the above as an example, now infer the arguments if any present in the paragraph given by user.
#     # """
    
#     # response = openai.ChatCompletion.create(
#     #     model=argument_finetuned_model,
#     #     messages=[{"role": "system", "content": argument_detection_prompt},
#     #               {"role": "user", "content": paragraph}]
#     # )
    
#     # argument_output = response["choices"][0]["message"]["content"]

#     # # if "No Argument Found" in argument_output:
#     # #     return {"message": "No argument detected in the paragraph."}

#     # extracted_claims = argument_output.split("\n")  # Assuming claims are line-separated
#     extracted_claims = paragraph.split('\n')

#     ### 🔹 Step 2: Atomize the Extracted Claims ###
#     atomized_claims = []
#     # print(f"argument model returns - {extracted_claims=}")
#     for claim in extracted_claims:
#         atomization_prompt = f"""
#         Break down the following claim into atomic facts.
#         Ensure each fact is self-contained, concise, and retains the original meaning.
#         Output should be a structured list of atomic claims.

#         Claim: {claim}
#         """
        
#         response = openai.ChatCompletion.create(
#             model=finetuned_models['atomizer_finetuned_model'],
#             messages=[{"role": "system", "content": "You are an AI that breaks down complex claims into atomic claims."},
#                       {"role": "user", "content": atomization_prompt}]
#         )
        
#         atomized_output = response["choices"][0]["message"]["content"]
#         atomized_claims.extend(atomized_output.split("\n"))  # Collecting all atomic claims

#     ### 🔹 Step 3: Generate Critical Perspectives ###
#     critical_thoughts = []

#     for atomic_claim in atomized_claims:
#         critique_prompt = f"""
#         Critically analyze the following atomic claim.
#         Provide alternative perspectives, question underlying assumptions, and explore potential biases.
#         Generate a structured critical assessment.

#         Atomic Claim: {atomic_claim}
#         """
        
#         response = openai.ChatCompletion.create(
#             model='gpt-3.5-turbo',
#             messages=[{"role": "system", "content": """Generate critical perspectives on claims given by user, challenge and expand claims by providing thought-provoking critiques. 
#                        for example, 
#                        Input: 'The one-child policy has been a major success, reducing overpopulation and improving China's economy. While controversial, most citizens support it, and studies show it has led to better healthcare for women. The government remains firm in its decision, arguing that any negative consequences are outweighed by long-term benefits.'
#                        Output: 'What are the ethical concerns about limiting family size? Is economic gain a justification for restricting personal freedoms?\n- How reliable are the studies supporting this policy? Are they government-funded, and do they account for hidden consequences like gender imbalance?\n- Are there long-term economic risks, such as an aging population and labor shortages, that counterbalance the short-term benefits?\n- The claim that 'most citizens support it'\u2014does this account for people who are afraid to speak against government policies?\n- What alternative policies could have achieved the same outcome with less human rights impact?'
#                        Similar to above critical line of thought to evaluate the presented argument, generate critical lines of thought for user given input. """},
#                       {"role": "user", "content": critique_prompt}]
#         )
        
#         critique_output = response["choices"][0]["message"]["content"]
#         critical_thoughts.append({"claim": atomic_claim, "critique": critique_output})
#     critique = '\n'.join(ct['critique'] for ct in critical_thoughts)
#     critique = critique.strip(' ').strip('-').strip('\n').strip(',')
#     # return {"original_text": paragraph, "critical_analysis": critical_thoughts}
#     return {"text": paragraph, "critique": critique}


import logging
import json
import yaml
import re
import openai
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    filename="server.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Load the config.yaml file
with open("models/config.yaml", "r") as file:
    config = yaml.safe_load(file)

openai.api_key = config["openai_key"]

finetuned_models = {
    "argument_finetuned_model": "ft:gpt-3.5-turbo-0125:personal::B3xAsgP1",
    "atomizer_finetuned_model": "ft:gpt-3.5-turbo-0125:personal::B3yyOMLV",
    "critical_fine_tuned_model": "ft:gpt-3.5-turbo-0125:personal::B3zr6iGR",
}

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["chrome-extension://ombijklbobodnojkjcbiohjdggnfikbc"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    paragraph: str


def preprocess(para, max_length=1000):
    """
    Truncate the paragraph to the nearest sentence ending occurring at or after max_length.
    """
    if len(para) <= max_length:
        return para.strip()

    match = re.search(r"[.!?]", para[max_length:])
    if match:
        return para[: max_length + match.start() + 1].strip()
    return para[:max_length].strip()


@app.get("/version")
def get_version():
    return {"version": "Unbias.me v1.1"}


@app.post("/analyze")
async def analyze_content(request: AnalyzeRequest):
    """
    Processes the input paragraph and returns a structured critical analysis.
    """
    try:
        # Log request data
        logger.info(f"Received request: {request.json()}")
        print(f"Received request: {request.json()}")

        paragraph = preprocess(request.paragraph)
        extracted_claims = paragraph.split("\n")

        # Step 2: Atomize Claims
        atomized_claims = []
        for claim in extracted_claims:
            atomization_prompt = f"""
            Break down the following claim into atomic facts.
            Ensure each fact is self-contained, concise, and retains the original meaning.
            Output should be a structured list of atomic claims.

            Claim: {claim}
            """
            response = openai.ChatCompletion.create(
                model=finetuned_models["atomizer_finetuned_model"],
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI that breaks down complex claims into atomic claims.",
                    },
                    {"role": "user", "content": atomization_prompt},
                ],
            )
            atomized_output = response["choices"][0]["message"]["content"]
            atomized_claims.extend(atomized_output.split("\n"))

        # Step 3: Generate Critical Perspectives
        critical_thoughts = []
        for atomic_claim in atomized_claims:
            critique_prompt = f"""
            Critically analyze the following atomic claim.
            Provide alternative perspectives, question underlying assumptions, and explore potential biases.
            Generate a structured critical assessment.

            Atomic Claim: {atomic_claim}
            """
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """Generate critical perspectives on claims given by the user. Challenge and expand claims by providing thought-provoking critiques.""",
                    },
                    {"role": "user", "content": critique_prompt},
                ],
            )
            critique_output = response["choices"][0]["message"]["content"]
            critical_thoughts.append({"claim": atomic_claim, "critique": critique_output})

        critique = "\n".join(ct["critique"] for ct in critical_thoughts).strip()

        response_data = {"text": paragraph, "critique": critique}

        # Log response data
        logger.info(f"Response: {json.dumps(response_data, indent=2)}")
        print(f"Response: {request.json()}")
        return response_data

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
