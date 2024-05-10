from flask import Flask, request, jsonify
import mysql.connector
from datetime import datetime
import logging


app = Flask(__name__)
logging.basicConfig(level=logging.INFO)



def get_db_connection():
    try:
        return mysql.connector.connect(
            host='localhost',
            user='root',
            password='password',
            database='sales'
        )
    except Exception as e:
        print(f"Database connection error: {e}")
        return None


@app.route('/', methods =['POST'])
def hendle_request():
    req = request.get_json()
    intent = req['queryResult']['intent']['displayName']
    user_query = req['queryResult']['queryText']
    session_id = req['session']
    response_text = ""

    if intent == "welcome":
        response_text = "Hello! Welcome to Virtual Height. May I know your name?"
        log_chat(session_id, user_query, intent, response_text)
    elif intent == "get_user_name":
        name = req['queryResult']['parameters'].get('name')
        response_text = f"Nice to meet you, {name}! Can I have your email address to assist you better?"
        save_user_name(session_id, name)
    elif intent == "get_user_email":
        for context in req['queryResult']['outputContexts']:
            if 'name' in context['parameters']:
                name = context['parameters']['name']
                break
        email = req['queryResult']['parameters'].get('email')
        response_text = f"Thank you {name}! Please Provide your Contact no?"
        save_user_email(session_id,name,email)
    elif intent == "get_user_phonenum":
        for context in req['queryResult']['outputContexts']:
            if 'name' in context['parameters']:
                name = context['parameters']['name']
            if 'email' in context['parameters']:
                email = context['parameters']['email']
        phonenum = req['queryResult']['parameters'].get('phonenum')
        response_text = f"Thank you, {name}! Please choose one of our services below:"
        save_user_details(session_id,name,phonenum,email)
        return jsonify({
            'fulfillmentText': response_text,
            'fulfillmentMessages': [
                {
                    'text': {'text': [response_text]}
                },
                {
                    'payload': {
                        'richContent': [
                            [
                                {
                                    'type': 'button',
                                    'icon': {
                                        'type': 'chevron_right',
                                        'color': '#FF9800'
                                    },
                                    'text': 'AI Services',
                                    'link': 'https://yourcompany.com/ai-services'
                                },
                                {
                                    'type': 'button',
                                        'icon': {
                                        'type': 'chevron_right',
                                        'color': '#FF9800'
                                    },
                                    'text': 'Web Development',
                                    'link': 'https://yourcompany.com/web-development'
                                },
                                {
                                    'type': 'button',
                                    'icon': {
                                        'type': 'chevron_right',
                                        'color': '#FF9800'
                                    },
                                    'text': 'DevOps Services',
                                    'link': 'https://yourcompany.com/devops-services'
                                },
                                {
                                    'type': 'button',
                                    'icon': {
                                        'type': 'chevron_right',
                                        'color': '#FF9800'
                                    },
                                    'text': 'Backend Services',
                                    'link': 'https://yourcompany.com/backend-services'
                                },
                                {
                                    'type': 'button',
                                    'icon': {
                                        'type': 'chevron_right',
                                        'color': '#FF9800'
                                    },
                                    'text': 'Design Services',
                                    'link': 'https://yourcompany.com/design-services'
                                },
                                {
                                    'type': 'button',
                                    'icon': {
                                        'type': 'chevron_right',
                                        'color': '#FF9800'
                                    },
                                    'text': 'Mobile App Development',
                                    'link': 'https://yourcompany.com/mobile-app-development'
                                }
                            ]
                        ]
                    }
                }
            ]
        })
    elif intent == "service_inquiry":
        service = req['queryResult']['parameters'].get('service')
        if service == "AI Services":
            response_text = "Our AI services include data analysis, machine learning model development, and AI consulting."
        elif service == "Web Development":
            response_text = "We provide full-stack web development, responsive design, and e-commerce solutions."
        elif service == "DevOps Services":
            response_text = "Our DevOps services include CI/CD pipeline setup, cloud infrastructure management, and automation."
        elif service == "Backend Services":
            response_text = "We specialize in API development, database management, and server-side scripting."
        elif service == "Design Services":
            response_text = "Our design services cover UX/UI design, graphic design, and branding."
        elif service == "Mobile App Development":
            response_text = "We develop native and cross-platform mobile apps for iOS and Android."
        else:
            response_text = "We offer a range of services including AI, web development, DevOps, backend services, design, and mobile app development. Which one would you like more information about?"

        log_chat(session_id, user_query, intent, response_text)

    return jsonify({'fulfillmentText': response_text})


def log_chat(session_id, user_query, intent, response_text):
    conn = get_db_connection()
    cursor = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    
    query = """
        INSERT INTO ChatLogs (session_id, user_query, intent, response_text, timestamp)
        VALUES (%s, %s, %s, %s, %s)
    """
    values = (session_id, user_query, intent, response_text, timestamp)

    try:
        cursor.execute(query, values)
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def save_user_name(session_id, name):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "INSERT INTO userdetails (user_id, name) VALUES (%s, %s) ON DUPLICATE KEY UPDATE name=%s"
    cursor.execute(query, (session_id, name, name))
    conn.commit()
    cursor.close()
    conn.close()


def save_user_email(session_id, name,email):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """INSERT INTO userdetails (user_id, name, email)
               VALUES (%s, %s, %s)
               ON DUPLICATE KEY UPDATE name=%s, email=%s"""
    cursor.execute(query, (session_id, name, email, name, email))
    conn.commit()
    cursor.close()
    conn.close()

def save_user_details(session_id, name, phonenum, email):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """INSERT INTO userdetails (user_id, name, phonenum, email)
               VALUES (%s, %s, %s, %s)
               ON DUPLICATE KEY UPDATE name=%s, phonenum=%s, email=%s"""
    cursor.execute(query, (session_id, name, phonenum, email, name, phonenum, email))
    conn.commit()
    cursor.close()
    conn.close()


if __name__ == '__main__':
    app.run(port=5000, debug=True)