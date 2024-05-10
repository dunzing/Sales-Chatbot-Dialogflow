from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
from serpapi import GoogleSearch
import os
import json
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
            database='flight'
        )
    except Error as e:
        print(f"Database connection error: {e}")
        return None


def format_date(date_input):
    if isinstance(date_input, list) and date_input:
        date_str = date_input[0]
    elif isinstance(date_input, str):
        date_str = date_input
    else:
        return None

    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError as e:
        logging.error("Date format error: %s", e)
        return None




@app.route('/', methods=['POST'])
def handleRequest():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"fulfillmentText": "No data received"}), 400

    try:
        intent = data['queryResult']['intent']['displayName']
        parameters = data['queryResult'].get('parameters', {})

        if intent == 'book.flight':
            source_city = parameters.get('source-city', [''])[0]
            destination_city = parameters.get('destination-city', [''])[0]
            departure_date = parameters.get('departure-date')[0] if isinstance(parameters.get('departure-date'), list) else parameters.get('departure-date')
            return_date = parameters.get('return-date')[0] if isinstance(parameters.get('return-date'), list) else parameters.get('return-date')

            flight_data = {
                "engine": "google_flights",
                "departure_id": source_city,
                "arrival_id": destination_city,
                "outbound_date": departure_date,
                "return_date": return_date,
                "currency": "INR",
                "hl": "en",
                "api_key": 'd689396f2cfe811bb8630f473260e01417cd5fb7589721559512d3a835c2e3f1'
            }

            search = GoogleSearch(flight_data)
            results = search.get_dict()
            flight_details = format_flight_details(results)

            return jsonify({
                "fulfillmentText": flight_details
            })

    except Exception as e:
        logging.error("Error: %s", str(e))
        return jsonify({"fulfillmentText": f"Error processing your request: {str(e)}"}), 500

    return jsonify({"fulfillmentText": "This intent is not supported by the webhook."})



def format_flight_details(results):
    flights = results.get('best_flights', [])
    if not flights:
        return "Sorry, no flights found based on your search criteria."

    outbound_date = results['search_parameters'].get('outbound_date', 'Unknown outbound date')
    return_date = results['search_parameters'].get('return_date', 'Unknown return date')

    response_text = f"✈️ Here are your flight details (Outbound: {outbound_date}, Return: {return_date}):\n\n"

    for idx, flight in enumerate(flights, start=1):
        flight_segments = flight.get('flights', [])
        flight_price = flight.get('price', 'N/A')

        response_text += f"{idx}. **Flight Details**\n"
        response_text += f"   Price: {flight_price}\n\n"

        for segment_idx, segment in enumerate(flight_segments, start=1):
            departure_airport = segment.get('departure_airport', {}).get('name', 'Unknown departure airport')
            arrival_airport = segment.get('arrival_airport', {}).get('name', 'Unknown arrival airport')
            departure_time = segment.get('departure_airport', {}).get('time', 'Unknown time')
            arrival_time = segment.get('arrival_airport', {}).get('time', 'Unknown time')
            airline = segment.get('airline', 'Unknown airline')
            flight_number = segment.get('flight_number', 'Unknown flight number')
            travel_class = segment.get('travel_class', 'Unknown class')
            duration = segment.get('duration', 'Unknown duration')


            response_text += f"     Airline: {airline} (Flight No: {flight_number})\n"
            response_text += f"     Departure: {departure_airport} at {departure_time}\n"
            response_text += f"     Arrival: {arrival_airport} at {arrival_time}\n"
            response_text += f"     Class: {travel_class}\n"
            response_text += f"     Duration: {duration} mins\n\n"

    return response_text.strip()





if __name__ == '__main__':
    app.run(debug=True)
