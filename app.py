from flask import Flask, request, jsonify, render_template
import sqlite3
import requests
import json
import os
import joblib
import pandas as pd
from dotenv import load_dotenv

from pydantic import BaseModel, Field


class Flight(BaseModel):
    origin: str
    destination: str
    flight_date: str
    price: float = Field(gt=0)
    airline: str

def validate_flight(flight):
    try:
        return Flight(**flight).model_dump()
    except Exception:
        return None

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

load_dotenv()

app = Flask(__name__)

DATABASE = "flightfinder.db"
JSON_FILE = "flights.json"


# External API configuration
# The API is ONLY used as a fallback for SQLite.
FLIGHT_API_URL = os.getenv("FLIGHT_API_URL", "")


# Optional RapidAPI configuration
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "")


# ---------------------------------------------------------
# ML Model
# ---------------------------------------------------------

MODEL_FILE = "ml/deployment_model.pkl"

fare_model = joblib.load(MODEL_FILE)


# ---------------------------------------------------------
# SQLite connection
# ---------------------------------------------------------

def get_db_connection():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


# ---------------------------------------------------------
# Database initialization
# ---------------------------------------------------------

def initialize_database():

    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS flights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            origin TEXT NOT NULL,
            destination TEXT NOT NULL,
            flight_date TEXT NOT NULL,
            price REAL NOT NULL,
            airline TEXT NOT NULL
        )
    """)

    # Index for our main search operation

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_flight_search
        ON flights(origin, destination, flight_date)
    """)

    # Index for route-based searches

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_route
        ON flights(origin, destination)
    """)

    conn.commit()

    conn.close()


# ---------------------------------------------------------
# ML FARE PREDICTION
# ---------------------------------------------------------

def predict_fare(flight):

    """
    Predict fare using the deployment ML model.

    The deployment model expects:

    - Airline
    - Source
    - Destination
    - Journey_Day
    - Journey_Month
    """

    try:

        flight_date = pd.to_datetime(
            flight["flight_date"]
        )

        prediction_data = pd.DataFrame({
            "Airline": [
                flight["airline"]
            ],

            "Source": [
                flight["origin"]
            ],

            "Destination": [
                flight["destination"]
            ],

            "Journey_Day": [
                flight_date.day
            ],

            "Journey_Month": [
                flight_date.month
            ]
        })

        predicted_price = fare_model.predict(
            prediction_data
        )[0]

        return round(float(predicted_price), 2)

    except Exception as error:

        print(
            "Fare prediction error:",
            error
        )

        return None


# ---------------------------------------------------------
# ADD ML PREDICTION TO FLIGHTS
# ---------------------------------------------------------

def add_predictions(flights):

    """
    Adds predicted_price to every flight.
    """

    for flight in flights:

        predicted_price = predict_fare(
            flight
        )

        flight["predicted_price"] = predicted_price

    return flights


# ---------------------------------------------------------
# JSON fallback
# ---------------------------------------------------------

def load_json_flights():

    try:

        with open(
            JSON_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except FileNotFoundError:

        print(
            "flights.json not found."
        )

        return []

    except json.JSONDecodeError:

        print(
            "flights.json contains invalid JSON."
        )

        return []


def search_json_fallback(
    origin,
    destination,
    date
):

    flights = load_json_flights()

    results = []

    for flight in flights:

        if (
            flight.get(
                "origin",
                ""
            ).upper() == origin

            and

            flight.get(
                "destination",
                ""
            ).upper() == destination

            and

            flight.get(
                "date",
                ""
            ) == date
        ):

            results.append({

                "origin":
                    flight.get("origin"),

                "destination":
                    flight.get("destination"),

                "flight_date":
                    flight.get("date"),

                "price":
                    flight.get("price"),

                "airline":
                    flight.get("airline")
            })

    results.sort(
        key=lambda flight: flight["price"]
    )

    return results


# ---------------------------------------------------------
# External API fallback
# ---------------------------------------------------------

def fetch_from_external_api(
    origin,
    destination,
    date
):


    if not FLIGHT_API_URL:

        print(
            "External API not configured."
        )

        return []

    try:

        params = {

            "origin":
                origin,

            "destination":
                destination,

            "date":
                date
        }

        headers = {}

        

        if RAPIDAPI_KEY:

            headers[
                "x-rapidapi-key"
            ] = RAPIDAPI_KEY

        if RAPIDAPI_HOST:

            headers[
                "x-rapidapi-host"
            ] = RAPIDAPI_HOST

        print(
            "Calling external flight API..."
        )

        response = requests.get(

            FLIGHT_API_URL,

            params=params,

            headers=headers,

            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        # Handle APIs returning:
        # {"data": [...]}

        if isinstance(data, dict):

            if isinstance(
                data.get("data"),
                list
            ):

                data = data["data"]

            elif isinstance(
                data.get("flights"),
                list
            ):

                data = data["flights"]

            else:

                data = []

        if not isinstance(
            data,
            list
        ):

            return []

        normalized_flights = []

        for flight in data:

            normalized_flight = (
                normalize_api_flight(
                    flight,
                    origin,
                    destination,
                    date
                )
            )

            if normalized_flight:

                normalized_flights.append(
                    normalized_flight
                )

        return normalized_flights

    except requests.RequestException as error:

        print(
            "External API request failed:",
            error
        )

        return []

    except ValueError as error:

        print(
            "Invalid API response:",
            error
        )

        return []

    except Exception as error:

        print(
            "External API error:",
            error
        )

        return []


# ---------------------------------------------------------
# API response normalization
# ---------------------------------------------------------

def normalize_api_flight(
    flight,
    origin,
    destination,
    date
):

    """
    Converts different possible API
    field names into our application's
    standard flight format.
    """

    if not isinstance(
        flight,
        dict
    ):

        return None

    flight_origin = (

        flight.get("origin")

        or

        flight.get("source")

        or

        origin
    )

    flight_destination = (

        flight.get("destination")

        or

        flight.get("dest")

        or

        destination
    )

    flight_date = (

        flight.get("date")

        or

        flight.get("flight_date")

        or

        date
    )

    price = (

        flight.get("price")

        or

        flight.get("fare")

        or

        flight.get("ticket_price")
    )

    airline = (

        flight.get("airline")

        or

        flight.get("flight")

        or

        flight.get("carrier")

        or

        "Unknown Airline"
    )

    if price is None:

        return None

    try:

        price = float(price)

    except (
        ValueError,
        TypeError
    ):

        return None

    return {

        "origin":
            str(
                flight_origin
            ).upper(),

        "destination":
            str(
                flight_destination
            ).upper(),

        "flight_date":
            str(
                flight_date
            ),

        "price":
            price,

        "airline":
            str(
                airline
            )
    }


# ---------------------------------------------------------
# Save API results into SQLite
# ---------------------------------------------------------

def save_flights_to_database(
    flights
):

    if not flights:

        return

    conn = get_db_connection()

    for flight in flights:

        conn.execute("""

            INSERT INTO flights

            (
                origin,
                destination,
                flight_date,
                price,
                airline
            )

            VALUES (?, ?, ?, ?, ?)

        """, (

            flight["origin"],

            flight["destination"],

            flight["flight_date"],

            flight["price"],

            flight["airline"]
        ))

    conn.commit()

    conn.close()


# ---------------------------------------------------------
# Search SQLite
# ---------------------------------------------------------

def search_database(
    origin,
    destination,
    date
):

    conn = get_db_connection()

    flights = conn.execute("""

        SELECT

            origin,

            destination,

            flight_date,

            price,

            airline

        FROM flights

        WHERE origin = ?

          AND destination = ?

          AND flight_date = ?

        ORDER BY price ASC

    """, (

        origin,

        destination,

        date

    )).fetchall()

    conn.close()

    validated_flights = []

    for flight in flights:
        validated_flight = validate_flight(dict(flight))
        if validated_flight:validated_flights.append(validated_flight)

    return validated_flights


# ---------------------------------------------------------
# Home page
# ---------------------------------------------------------

@app.route("/")
def home():

    return render_template(
        "home.html"
    )


# ---------------------------------------------------------
# Search page
# ---------------------------------------------------------

@app.route("/search")
def search_page():

    return render_template(
        "index.html"
    )


# ---------------------------------------------------------
# Flight search API
# ---------------------------------------------------------

@app.route("/api/flights")
def get_flights():

    origin = request.args.get(
        "origin",
        ""
    ).strip().upper()

    destination = request.args.get(
        "destination",
        ""
    ).strip().upper()

    date = request.args.get(
        "date",
        ""
    ).strip()


    # Validate inputs

    if (
        not origin
        or not destination
        or not date
    ):

        return jsonify({

            "error":
                "origin, destination and date are required"

        }), 400


    # -----------------------------------------------------
    # STEP 1: SQLite
    # -----------------------------------------------------

    try:

        database_results = search_database(

            origin,

            destination,

            date
        )

        # SQLite has the requested data

        if database_results:

            print(

                f"SQLite: "
                f"{len(database_results)} "
                f"flight(s) found."

            )

            # Add ML predictions

            database_results = add_predictions(
                database_results
            )

            return jsonify(
                database_results
            )

        print(
            "SQLite: no matching flights found."
        )

    except Exception as error:

        print(
            "SQLite error:",
            error
        )


    # -----------------------------------------------------
    # STEP 2: External API fallback
    # -----------------------------------------------------

    api_results = fetch_from_external_api(

        origin,

        destination,

        date
    )

    if api_results:

        print(

            f"External API: "
            f"{len(api_results)} "
            f"flight(s) found."

        )

        # Cache API results in SQLite

        try:

            save_flights_to_database(
                api_results
            )

            print(
                "API results saved to SQLite."
            )

        except Exception as error:

            print(

                "Could not save API results "
                "to SQLite:",

                error
            )


        # Add ML predictions

        api_results = add_predictions(
            api_results
        )

        return jsonify(
            api_results
        )

    print(
        "External API: no results."
    )


    # -----------------------------------------------------
    # STEP 3: JSON fallback
    # -----------------------------------------------------

    json_results = search_json_fallback(

        origin,

        destination,

        date
    )

    if json_results:

        print(

            f"JSON fallback: "
            f"{len(json_results)} "
            f"flight(s) found."

        )

        # Add ML predictions

        json_results = add_predictions(
            json_results
        )

        return jsonify(
            json_results
        )


    # -----------------------------------------------------
    # Nothing found
    # -----------------------------------------------------

    return jsonify([])


# ---------------------------------------------------------
# Database statistics
# ---------------------------------------------------------

@app.route("/api/stats")
def database_stats():

    try:

        conn = get_db_connection()

        total_flights = conn.execute("""

            SELECT COUNT(*) AS count

            FROM flights

        """).fetchone()["count"]


        airlines = conn.execute("""

            SELECT COUNT(
                DISTINCT airline
            ) AS count

            FROM flights

        """).fetchone()["count"]


        routes = conn.execute("""

            SELECT COUNT(
                DISTINCT origin || '-' || destination
            ) AS count

            FROM flights

        """).fetchone()["count"]


        conn.close()

        return jsonify({

            "total_flights":
                total_flights,

            "airlines":
                airlines,

            "routes":
                routes
        })

    except Exception as error:

        return jsonify({

            "error":
                str(error)

        }), 500


# ---------------------------------------------------------
# Application startup
# ---------------------------------------------------------

if __name__ == "__main__":

    initialize_database()

    print(
        "----------------------------------------"
    )

    print(
        "Flight Fare Comparison Backend"
    )

    print(
        "----------------------------------------"
    )

    print(
        "Database:",
        DATABASE
    )

    print(

        "External API fallback:",

        "Configured"
        if FLIGHT_API_URL
        else
        "Not configured"
    )

    print(
        "ML Model:",
        MODEL_FILE
    )

    print(
        "----------------------------------------"
    )

    app.run(
        debug=True
    )