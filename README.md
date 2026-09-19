Flightz ✈️ 💰 🗄️
A full-stack flight fare comparison system built with Flask, SQLite, Pydantic, and Machine Learning. Flightz allows users to search flights by route and date, compare available fares, and view ML-based estimated fares through a simple web interface.

The system uses SQLite as the primary flight data source, with an external API and JSON dataset implemented as fallback mechanisms. Flight records are validated before being processed, and API results can be cached into the database for future searches

Table of Contents
Overview
Key Features
Technology Stack


Overview

Flightz is a web-based flight fare comparison application designed to demonstrate the integration of backend development, database systems, data validation, fallback data sources, and machine learning.

Users can enter an origin, destination, and travel date to search for available flights. The application retrieves flight records from SQLite, validates the returned data using Pydantic, and applies a trained machine learning model to generate an estimated fare.

The backend also includes an external flight API fallback and a local JSON fallback. API results, when available, can be stored in SQLite so that subsequent searches can use the database instead of repeatedly requesting the external service.

Key Features

✈️ Flight Search — Search flights using origin, destination, and travel date.
🗄️ SQLite Database — Stores and retrieves flight records locally.
⚡ Indexed Database Queries — Uses a composite database index for efficient flight searches.
🛡️ Pydantic Validation — Validates flight records before they are processed by the application.
🤖 ML Fare Estimation — Uses a trained Random Forest model to estimate flight fares.
🔄 Fallback Architecture — Uses an external API and JSON data as fallback sources when database results are unavailable.
💾 API Result Caching — External API results can be stored in SQLite for subsequent searches.
📊 Performance Benchmarking — Compares indexed SQLite searches against full in-memory dataset scans.
🔐 Environment Configuration — API credentials and configuration are stored using environment variables.
🌐 Flask Backend — Provides the application and flight-search API.
🎨 Web Interface — Provides login and flight-search pages with a responsive frontend.

Technology Stack

Backend

Python
Flask — Web framework and REST API
SQLite — Relational database
Pydantic — Data validation and schema enforcement
Requests — External API communication
python-dotenv — Environment variable management

Machine Learning

Pandas — Data processing
NumPy — Numerical processing
Scikit-learn — Machine learning model training
Joblib — Model serialization

Frontend

HTML5
CSS3
JavaScript






