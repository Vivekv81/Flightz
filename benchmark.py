import sqlite3
import time
import statistics

DATABASE = "flightfinder.db"

ORIGIN = "GOA"
DESTINATION = "DELHI"
DATE = "2027-06-10"

ITERATIONS = 1000


# ============================================================
# LOAD DATA FROM SQLITE
# ============================================================

def load_data_from_sqlite():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    rows = connection.execute("""
        SELECT
            origin,
            destination,
            flight_date,
            price,
            airline
        FROM flights
    """).fetchall()

    connection.close()

    return [dict(row) for row in rows]


# ============================================================
# SQLITE SEARCH
# ============================================================

def search_sqlite():
    connection = sqlite3.connect(DATABASE)

    rows = connection.execute("""
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
        ORIGIN,
        DESTINATION,
        DATE
    )).fetchall()

    connection.close()

    return rows


# ============================================================
# JSON-LIKE LIST SEARCH
# ============================================================

def search_json(data):
    results = []

    for flight in data:

        if (
            flight["origin"] == ORIGIN
            and flight["destination"] == DESTINATION
            and flight["flight_date"] == DATE
        ):
            results.append(flight)

    results.sort(key=lambda flight: flight["price"])

    return results


# ============================================================
# BENCHMARK FUNCTION
# ============================================================

def benchmark(function, *args):

    times = []

    result_count = 0

    for _ in range(ITERATIONS):

        start = time.perf_counter()

        results = function(*args)

        end = time.perf_counter()

        times.append((end - start) * 1000)

        result_count = len(results)

    return {
        "count": result_count,
        "average": statistics.mean(times),
        "median": statistics.median(times),
        "minimum": min(times),
        "maximum": max(times)
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 60)
    print("FLIGHT SEARCH PERFORMANCE BENCHMARK")
    print("=" * 60)

    print()
    print("Search:")
    print("Origin       :", ORIGIN)
    print("Destination  :", DESTINATION)
    print("Date         :", DATE)
    print()
    print("Iterations   :", ITERATIONS)

    # Load the exact same dataset from SQLite
    # and use it as our JSON-equivalent in-memory dataset.
    data = load_data_from_sqlite()

    print()
    print("Dataset size :", len(data), "records")

    # --------------------------------------------------------
    # SQLITE
    # --------------------------------------------------------

    sqlite_result = benchmark(search_sqlite)

    print()
    print("-" * 60)
    print("SQLite")
    print("-" * 60)

    print("Results found :", sqlite_result["count"])
    print("Average       :", f'{sqlite_result["average"]:.4f} ms')
    print("Median        :", f'{sqlite_result["median"]:.4f} ms')
    print("Minimum       :", f'{sqlite_result["minimum"]:.4f} ms')
    print("Maximum       :", f'{sqlite_result["maximum"]:.4f} ms')

    # --------------------------------------------------------
    # JSON / IN-MEMORY LIST
    # --------------------------------------------------------

    json_result = benchmark(search_json, data)

    print()
    print("-" * 60)
    print("JSON / In-Memory List")
    print("-" * 60)

    print("Results found :", json_result["count"])
    print("Average       :", f'{json_result["average"]:.4f} ms')
    print("Median        :", f'{json_result["median"]:.4f} ms')
    print("Minimum       :", f'{json_result["minimum"]:.4f} ms')
    print("Maximum       :", f'{json_result["maximum"]:.4f} ms')

    # --------------------------------------------------------
    # SPEEDUP
    # --------------------------------------------------------

    if sqlite_result["average"] > 0:

        speedup = (
            json_result["average"]
            / sqlite_result["average"]
        )

        print()
        print("-" * 60)
        print("Performance Comparison")
        print("-" * 60)

        print(
            f"SQLite speedup: {speedup:.2f}x"
        )

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()