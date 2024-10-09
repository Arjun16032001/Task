import sqlite3
import json
 
# def create_database():
#     conn = sqlite3.connect('chat.db')
#     cursor = conn.cursor()
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS chat (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             entities TEXT,
#             entity TEXT,
#             matched_question TEXT NOT NULL,
#             message TEXT NOT NULL,
#             question_type TEXT NOT NULL
#         )
#     ''')
#     conn.commit()
#     conn.close()
 # Connecting to sqlite
# connection object
connection_obj = sqlite3.connect('chat.db')
 
# cursor object
cursor_obj = connection_obj.cursor()
 
# Drop the GEEK table if already exists.
cursor_obj.execute("DROP TABLE IF EXISTS CHAT")
 
# Creating table
table = '''
        CREATE TABLE IF NOT EXISTS chat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entities TEXT,
            entity TEXT,
            matched_question TEXT NOT NULL,
            message TEXT NOT NULL,
            question_type TEXT NOT NULL
        )'''
 
cursor_obj.execute(table)
 
print("Table is Ready")
 
# Close the connection
connection_obj.close()
 
def insert_chat(entities, entity, matched_question, message, question_type):
    try:
        conn = sqlite3.connect('chat.db')
        cursor = conn.cursor()
       
        cursor.execute('''
            INSERT INTO chat (entities, entity, matched_question, message, question_type)
            VALUES (?, ?, ?, ?, ?)
        ''', (entities, entity, matched_question, message, question_type))
       
        conn.commit()
       
        inserted_id = cursor.lastrowid
        conn.close()
       
        return inserted_id
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return None
 
# def insert_chat(entities, entity, matched_question, message, question_type):
#     try:
#         conn = sqlite3.connect('chat.db')
#         cursor = conn.cursor()
       
#         cursor.execute('''
#             INSERT INTO chat (entities, entity, matched_question, message, question_type)
#             VALUES (?, ?, ?, ?, ?)
#         ''', (entities, entity, matched_question, message, question_type))
       
#         conn.commit()
       
#         inserted_id = cursor.lastrowid
       
#         conn.close()
#         return inserted_id
 
#     except sqlite3.Error as e:
#         print(f"Database error: {e}")
#         return None  # Handle the error properly, return a meaningful response
 
 
 
def get_chat(message_id):
    conn = sqlite3.connect('chat.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM chat WHERE id = ?
    ''', (message_id,))
    result = cursor.fetchone()
    conn.close()
 
    if result is None:
        # Handle the case where no record is found
        return {"status": "error", "message": f"No chat found with ID {message_id}"}
   
    return {
        "id": result[0],
        "entities": result[1],
        "entity": result[2],
        "matched_question": result[3],
        "message": result[4],
        "question_type": result[5]
    }
 
 
# create_database()
# insert_chat(json.dumps({
#     "grade": "grade 9",
#     "current_academic_year": "null"
#   }), "current_academic_year", json.dumps({
#     "question": "I would need fee details for grade 11 for 2023-2024",
#     "answer": "Select * from fee where grade is {grade} and current_academic_year is {current_academic_year}",
#     "entities": [
#       "grade",
#       "current_academic_year"
#     ],
#     "sub_questions": {
#       "current_academic_year": "Could you please provide the academic year? (eg: 2023-2024) : ",
#       "grade": "Could you please provide the grade? (eg: 11th Grade) : "
#     },
#     "type": {
#       "current_academic_year": "DATE",
#       "grade": "NUM"
#     }
#   }), "Could you please provide the academic year? (eg: 2023-2024) : ", "sub_question")
 
# {
#   "status": "success",
#   "message": "",
#   "question_type": "",
#   "entity": "current_academic_year",
#   "entities": {
#     "grade": "grade 9",
#     "current_academic_year": "null"
#   },
#   "matched_question": {
#     "question": "I would need fee details for grade 11 for 2023-2024",
#     "answer": "Select * from fee where grade is {grade} and current_academic_year is {current_academic_year}",
#     "entities": [
#       "grade",
#       "current_academic_year"
#     ],
#     "sub_questions": {
#       "current_academic_year": "Could you please provide the academic year? (eg: 2023-2024) : ",
#       "grade": "Could you please provide the grade? (eg: 11th Grade) : "
#     },
#     "type": {
#       "current_academic_year": "DATE",
#       "grade": "NUM"
#     }
#   }
# }
 