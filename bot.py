import json
import re
import spacy
 
# Load the model once at the beginning of your script

nlp = spacy.load("model-best")
nlp1=spacy.load("en_core_web_md")
 
ENTITY_MAPPING = {
    "grade": "GRADE",
    "current_academic_year": "ACADEMIC_YEAR"
}
 
# Load the JSON data from a file
def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)
 
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
 
 
# Validate grade input
# def validate_grade(grade_input):
#     grade_pattern = r"\d{1,2}(st|nd|rd|th)\s(Standard|Grade|Class)|Grade\s\d{1,2}|Class\s\d{1,2}"
#     return re.match(grade_pattern, grade_input, re.IGNORECASE) is not None
 
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
 
    # Loop through the current doc entities
    doc = nlp(user_input)
    for doc in doc.ents:
        doc_entities[doc.label_] = doc.text
 
    for entity in required_entities:
        print(f"Entity: {entity}")
        # Fill extracted_entities with values from doc_entities based on ENTITY_MAPPING
        if entity in ENTITY_MAPPING:
            entity_label = ENTITY_MAPPING[entity]
            extracted_entities[entity] = doc_entities.get(entity_label, None)  # Get value or None if not found
 
    return extracted_entities
 
 
def fill_missing_entities(missing_entities, required_entities, sub_questions, entity_types):
    for entity in required_entities:
        while True:
            # If the entity is missing, prompt the user using sub_questions
            if missing_entities.get(entity) is None:
                prompt = sub_questions.get(entity, f"Please provide the {entity.replace('_', ' ')}: ")
                user_input = input(prompt)
 
                # Determine the type of the entity
                entity_type = entity_types.get(entity)
 
                # Validate the input based on the entity type from JSON
                if entity_type == "ACADEMIC_YEAR":
                    if validate_academic_year(user_input):
                        missing_entities[entity] = user_input
                        break
                    else:
                        print(f"The {entity.replace('_', ' ')} provided is invalid. Please try again.")
                elif entity_type == "NUM":
                    if validate_numeric(user_input):  # Using the new numeric validator
                        missing_entities[entity] = user_input
                        break
                    else:
                        print(f"The {entity.replace('_', ' ')} provided is invalid. Please try again.")
                else:
                    # If no specific validation exists, accept the input as is
                    missing_entities[entity] = user_input
                    break
            else:
                break
 
    return missing_entities
 
def extract_numeric(value):
    # Use regex to find all digits in the string
    match = re.search(r'\d+', value)
    return match.group(0) if match else None
 
 
def validate_and_convert_entities(extracted_entities, entity_types):
    validated_entities = {}
 
    for entity, value in extracted_entities.items():
        entity_type = entity_types.get(entity)
 
        if entity_type == "ACADEMIC_YEAR":
            # Convert the academic year format
            converted_year = value
            if converted_year:
                validated_entities[entity] = converted_year
            else:
                print(f"The academic year '{value}' is invalid. Please provide a valid format (YYYY-YY).")
        elif entity_type == "NUM":
            # Extract the numeric value from the string
            extracted_number = extract_numeric(value)
            if extracted_number:
                validated_entities[entity] = extracted_number
            else:
                print(f"The value '{value}' for {entity.replace('_', ' ')} is invalid. Please provide a valid number.")
        else:
            # If no specific validation exists, accept the input as is
            validated_entities[entity] = value
 
    return validated_entities
 
def handle_query(user_input):
    json_data = load_json('queries.json')  # Load the JSON data from the file
   
    matched_question = get_most_similar_question(user_input, json_data)
 
    # Check if a match was found
    if matched_question is None:
        print("I'm sorry, but I couldn't find an answer to your question. Can you please rephrase it?")
        return
   
    print(f"Matched Question: {matched_question["question"]}")
    if "entities" in matched_question:  
     extracted_entities = extract_entities(user_input, matched_question["entities"])
     print(f"Extracted entities: {extracted_entities}")  # Debug print
    
     filled_entities = fill_missing_entities(extracted_entities, matched_question["entities"], matched_question.get("sub_questions", {}), matched_question.get("type", {}))
     print(f"Filled entities: {filled_entities}")  # Debug print
  
     validated_entities = validate_and_convert_entities(filled_entities, matched_question.get("type", {}))
     print(f"Validated entities: {validated_entities}")  # Debug print
    if "entities" in matched_question:   
     query = matched_question["answer"].format(**validated_entities)
     return query
    else:
        query=matched_question["answer"]
        return query
 
def chatbot():
    print("Welcome to the Academic Query Chatbot! Type 'exit' to quit.")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'exit':
            print("Chatbot: Thank you for chatting! Goodbye.")
            break
        
        result = handle_query(user_input)
        print(f"Chatbot: {result}")

# Start the chatbot
if __name__ == "__main__":
    chatbot()