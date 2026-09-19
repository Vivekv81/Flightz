import sqlite3
import random
from datetime import datetime, timedelta


# ============================================================
# CONFIGURATION
# ============================================================

DATABASE = "flightfinder.db"

START_DATE = "2026-01-01"
END_DATE = "2027-06-30"

CITIES = [
    "DELHI",
    "MUMBAI",
    "GOA",
    "BANGALORE"
]

AIRLINES = [
    "Air India",
    "IndiGo",
    "Vistara",
    "SpiceJet"
]

FLIGHTS_PER_ROUTE = 4


# ============================================================
# CREATE DATABASE
# ============================================================

def create_database():

    connection = sqlite3.connect(DATABASE)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS flights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            origin TEXT NOT NULL,
            destination TEXT NOT NULL,
            flight_date TEXT NOT NULL,
            price REAL NOT NULL,
            airline TEXT NOT NULL
        )
    """)

    connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_flight_search
        ON flights(origin, destination, flight_date)
    """)

    connection.commit()

    return connection


# ============================================================
# GENERATE DATES
# ============================================================

def get_dates():

    start = datetime.strptime(START_DATE, "%Y-%m-%d")
    end = datetime.strptime(END_DATE, "%Y-%m-%d")

    dates = []

    current = start

    while current <= end:
        dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)

    return dates


# ============================================================
# GENERATE ROUTES
# ============================================================

def get_routes():

    routes = []

    for origin in CITIES:

        for destination in CITIES:

            if origin != destination:
                routes.append((origin, destination))

    return routes


# ============================================================
# GENERATE PRICE
# ============================================================

def generate_price():

    return random.randint(3000, 12000)


# ============================================================
# SEED DATABASE
# ============================================================

def seed_database():

    connection = create_database()

    cursor = connection.cursor()

    # Remove previous data
    cursor.execute("DELETE FROM flights")

    dates = get_dates()
    routes = get_routes()

    records = []

    for date in dates:

        for origin, destination in routes:

            for _ in range(FLIGHTS_PER_ROUTE):

                airline = random.choice(AIRLINES)
                price = generate_price()

                records.append((
                    origin,
                    destination,
                    date,
                    price,
                    airline
                ))

    cursor.executemany("""
        INSERT INTO flights
        (
            origin,
            destination,
            flight_date,
            price,
            airline
        )
        VALUES (?, ?, ?, ?, ?)
    """, records)

    connection.commit()

    # Get total number of records
    cursor.execute("SELECT COUNT(*) FROM flights")

    total_records = cursor.fetchone()[0]

    connection.close()

    print()
    print("=" * 45)
    print("DATABASE SEEDED SUCCESSFULLY")
    print("=" * 45)
    print("Database       :", DATABASE)
    print("Date range     :", START_DATE, "to", END_DATE)
    print("Cities         :", len(CITIES))
    print("Routes         :", len(routes))
    print("Flights/route  :", FLIGHTS_PER_ROUTE)
    print("Total records  :", total_records)
    print("=" * 45)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    seed_database()