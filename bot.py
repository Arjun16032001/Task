import json
import re
import spacy
from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from chat import insert_chat, get_chat
from sentence_transformers import SentenceTransformer, util
import torch


# Request body model for input
class SentenceRequest(BaseModel):
    input_sentence: str  # Only one input sentence now
    message_id: str
    # question_type: str
    # entity: Optional[str] = None
    # entities: Optional[dict] = None
    # matched_question: Optional[dict] = None

# Load the model once at the beginning of your script
nlp = spacy.load("model-best")
nlp1 = spacy.load("en_core_web_md")
# Load the model once at the beginning of your script
model = SentenceTransformer('all-MiniLM-L6-v2')

app = FastAPI()

# Define CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins; for production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ENTITY_MAPPING = {
    "grade": "GRADE",
    "current_academic_year": "ACADEMIC_YEAR"
}

# Load the JSON data from a file
def load_json(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the file: {file_path}")
        return []
    
# # Function to get the most similar question
# def get_most_similar_question(user_input, json_data, threshold=0.8):
#     # Encode the user input and the questions from json_data
#     user_input_embedding = model.encode(user_input, convert_to_tensor=True)
   
#     # Create a list of question embeddings
#     questions = [item["question"] for item in json_data]
   
#     questions_embeddings = model.encode(questions, convert_to_tensor=True)
#     # Calculate cosine similarities
#     cosine_scores = util.pytorch_cos_sim(user_input_embedding, questions_embeddings)
 
#     # Get the best match
#     best_score, best_index = torch.max(cosine_scores, dim=1)
   
#     # Check if the best score meets the threshold
#     if best_score < threshold:
#         return None  # No match found
 
#     return json_data[best_index.item()]  # Return the best matched question
# Function to get the most similar question
def get_most_similar_question(user_input, json_data, threshold=0.8):
    user_input_doc = nlp1(user_input)
    
    best_score = 0.0
    best_match = None
    
    for item in json_data:
        question_doc = nlp1(item["question"])
        score = user_input_doc.similarity(question_doc)
        
        if score > best_score:
            best_score = score
            best_match = item

    if best_score < threshold:
        return None  # No match found

    return best_match  # Return the best matched question

# Numeric validator function
def validate_numeric(input_value):
    return re.fullmatch(r'\d+', input_value) is not None

# Validate academic year input
def validate_academic_year(year_input):
    year_pattern = r'\d{4}-\d{4}'
    return re.match(year_pattern, year_input) is not None

# Function to extract entities (grade and year) based on required entities from matched question
def extract_entities(user_input, required_entities):
    extracted_entities = {}
    doc_entities = {}

    # Process the document
    doc = nlp(user_input)
    for ent in doc.ents:
        doc_entities[ent.label_] = ent.text

    for entity in required_entities:
        print(f"Entity: {entity}")
        # Fill extracted_entities with values from doc_entities based on ENTITY_MAPPING
        if entity in ENTITY_MAPPING:
            entity_label = ENTITY_MAPPING[entity]
            extracted_entities[entity] = doc_entities.get(entity_label, None)  # Get value or None if not found

    return extracted_entities

# def fill_missing_entities(missing_entities, required_entities, sub_questions, entity_types):
#     for entity in required_entities:
#         while True:
#             # If the entity is missing, prompt the user using sub_questions
#             if missing_entities.get(entity) is None:
#                 prompt = sub_questions.get(entity, f"Please provide the {entity.replace('_', ' ')}: ")
#                 user_input = input(prompt)
 
#                 # Determine the type of the entity
#                 entity_type = entity_types.get(entity)
 
#                 # Validate the input based on the entity type from JSON
#                 if entity_type == "ACADEMIC_YEAR":
#                     if validate_academic_year(user_input):
#                         missing_entities[entity] = user_input
#                         break
#                     else:
#                         print(f"The {entity.replace('_', ' ')} provided is invalid. Please try again.")
#                 elif entity_type == "NUM":
#                     if validate_numeric(user_input):  # Using the new numeric validator
#                         missing_entities[entity] = user_input
#                         break
#                     else:
#                         print(f"The {entity.replace('_', ' ')} provided is invalid. Please try again.")
#                 else:
#                     # If no specific validation exists, accept the input as is
#                     missing_entities[entity] = user_input
#                     break
#             else:
#                 break
 
#     return missing_entities

def extract_numeric(value):
    # Use regex to find all digits in the string
    match = re.search(r'\d+', value)
    return match.group(0) if match else None

# def validate_and_convert_entities(extracted_entities, entity_types):
#     validated_entities = {}

#     for entity, value in extracted_entities.items():
#         entity_type = entity_types.get(entity)

#         if entity_type == "ACADEMIC_YEAR":
#             # Convert the academic year format
#             converted_year = value
#             if converted_year and validate_academic_year(converted_year):
#                 validated_entities[entity] = converted_year
#             else:
#                 print(f"The academic year '{value}' is invalid. Please provide a valid format (YYYY-YYYY).")
#         elif entity_type == "NUM":
#             # Extract the numeric value from the string
#             extracted_number = extract_numeric(value)
#             if extracted_number and validate_numeric(extracted_number):
#                 validated_entities[entity] = extracted_number
#             else:
#                 print(f"The value '{value}' for {entity.replace('_', ' ')} is invalid. Please provide a valid number.")
#         else:
#             # If no specific validation exists, accept the input as is
#             validated_entities[entity] = value

#     return validated_entities

def build_answer(extracted_entities, matched_question):
    missed_one = None
 
    # Test if the issue is with DB connection or insert
    try:
        for entity in extracted_entities:
            if(extracted_entities[entity] is None and missed_one is None):
                missed_one = entity
 
        # return {"status": "success", "message_id": "1", "message": "Hello"}
        if missed_one is None:
            query = matched_question["answer"].format(**extracted_entities)
           
            print(f"Resulting Query: {query}")  # Debug print
            id = insert_chat(json.dumps(extracted_entities), "null" , json.dumps(matched_question), query, "question")
            if id is None:
                return {"status": "error", "message": "DB Insert failed"}
            print(f"Inserted ID: {id}")  # Debug print
            return {"status": "success",  "message_id": id, "message": query}
        else:
            match_q = matched_question.get("sub_questions", {})
            question = match_q.get(missed_one, f"Please provide the {missed_one.replace('_', ' ')}: ")
            id = insert_chat(json.dumps(extracted_entities), missed_one, json.dumps(matched_question), question, "sub_question")
            if id is None:
                return {"status": "error", "message": "DB Insert failed"}
            print(f"Inserted ID: {id}")  # Debug print
            return {"status": "success", "message_id": id, "message": question}
 
    except Exception as e:
        print(f"Error in build_answer: {e}")
        return {"status": "error", "message": str(e)}

def handle_query1(user_input):
    json_data = load_json('queries.json')  # Load the JSON data from the file
   
    matched_question = get_most_similar_question(user_input, json_data)
 
    # Check if a match was found
    if matched_question is None:
        return {"status": "success", "message_id":"start", "message": "I'm sorry, but I couldn't find an answer to your question. Can you please rephrase it?"}
        
   
    print(f"Matched Question: {matched_question["question"]}")
 
    extracted_entities = extract_entities(user_input, matched_question["entities"])
    print(f"Extracted entities: {extracted_entities}")  # Debug print
 
    return build_answer(extracted_entities, matched_question)
 
    # filled_entities = fill_missing_entities(extracted_entities, matched_question["entities"], matched_question.get("sub_questions", {}), matched_question.get("type", {}))
    # print(f"Filled entities: {filled_entities}")  # Debug print
 
    # validated_entities = validate_and_convert_entities(filled_entities, matched_question.get("type", {}))
    # print(f"Validated entities: {validated_entities}")  # Debug print
   
    # query = matched_question["answer"].format(**validated_entities)
 
 
 
 
# Example user input
# user_input = "What are fee details for the Grade 11 academic year 2023-24?"
# handle_query(user_input)
 
 
def handle_sub_question(user_input, entity, entities, matched_question):
    entities[entity] = user_input
    new_entities = entities
    return build_answer(new_entities, matched_question)
 
@app.post("/handle_query")
async def process_sentence(request: SentenceRequest):
    input_sentence = request.input_sentence
    message_id = request.message_id

    if input_sentence.lower()=="exit":
        return {"status": "success", "message": "Thank you for chatting! Goodbye!"}
 
    if(message_id == "start" ):
        question_type = "question"
    else:
        chat = get_chat(message_id)
        question_type = chat.get("question_type", "sub_question")
        print(question_type)
 
    # return {"status": "success", "message": "Test", "type": "question"}
 
    try:
        if(question_type == "question"):
            query = handle_query1(input_sentence)
            return query
        elif(question_type == "sub_question"):
            query = handle_sub_question(input_sentence, chat.get('entity', ""), json.loads(chat.get('entities', [])), json.loads(chat.get('matched_question', {})))
            return query
            # return {"status": "success", "message": "Test", "type": "question"}
        else:
            return {"status": "error", "message": "Invalid type", "type": "error"}
    except Exception as e:
        print(f"Error in process_sentence: {e}")
        raise HTTPException(status_code=500, detail=str(e))
 
 