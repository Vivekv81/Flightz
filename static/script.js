// 🔹 LOGIN FUNCTION

function login() {

    const email = document.getElementById("email").value;

    const password = document.getElementById("password").value;

    const errorMessage = document.getElementById("error-message");

    // Dummy credentials

    const validEmail = "testuser@example.com";

    const validPassword = "Test@1234";

    if (email === validEmail && password === validPassword) {

        localStorage.setItem("loggedIn", "true");

        window.location.href = "/";

    } else {

        errorMessage.innerText = "Invalid email or password!";

        errorMessage.style.color = "red";

    }

}


// 🔹 CHECK LOGIN STATUS

if (window.location.pathname === "/") {

    if (localStorage.getItem("loggedIn") !== "true") {

        window.location.href = "/search";

    }

}


// 🔹 SEARCH FLIGHTS FUNCTION

// ============================================================

// FLIGHT SEARCH

// ============================================================

async function searchFlights() {

    const origin = document.getElementById("origin").value.trim();

    const destination = document.getElementById("destination").value.trim();

    const date = document.getElementById("date").value;

    const results = document.getElementById("results");

    // Validate inputs

    if (!origin || !destination || !date) {

        results.innerHTML = `

            <p>Please enter origin, destination and date.</p>

        `;

        return;

    }

    // Loading message

    results.innerHTML = `

        <p>Searching for flights...</p>

    `;

    try {

        const params = new URLSearchParams({

            origin: origin.toUpperCase(),

            destination: destination.toUpperCase(),

            date: date

        });

        const response = await fetch(

            `/api/flights?${params.toString()}`

        );

        if (!response.ok) {

            throw new Error(`Server returned ${response.status}`);

        }

        const flights = await response.json();

        console.log("Flights received from backend:", flights);

        // No results

        if (!Array.isArray(flights) || flights.length === 0) {

            results.innerHTML = `

                <p>No flights found for this route and date.</p>

            `;

            return;

        }

        // Clear loading message

        results.innerHTML = "";

        // Display flights

        flights.forEach(flight => {

            const card = document.createElement("div");

            card.className = "flight-card";

            // Support both "flight_date" and "date"

            const flightDate =

                flight.flight_date || flight.date || date;

            card.innerHTML = `

                <p>

                    <strong>Airline:</strong>

                    ${flight.airline || "Unknown"}

                </p>

                <p>

                    <strong>From:</strong>

                    ${flight.origin || origin.toUpperCase()}

                </p>

                <p>

                    <strong>To:</strong>

                    ${flight.destination || destination.toUpperCase()}

                </p>

                <p>

                    <strong>Date:</strong>

                    ${flightDate}

                </p>

                <p>
                <strong>Price:</strong>
                ₹${flight.price}
                </p>

                <p>
                <strong>Estimated Fare:</strong>
                ₹${flight.predicted_price}
                </p>

            `;

            results.appendChild(card);

        });

    } catch (error) {

        console.error("Flight search error:", error);

        results.innerHTML = `

            <p>

                Unable to search flights.

                Please try again.

            </p>

        `;

    }

}


// 🔹 ENABLE LOGIN ON "ENTER" KEY PRESS

document.addEventListener("keypress", function (event) {

    if (event.key === "Enter") {

        const email = document.getElementById("email");

        const password = document.getElementById("password");

        if (email && password) {

            login();

        }

    }

});