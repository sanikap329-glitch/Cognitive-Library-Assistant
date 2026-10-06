document.addEventListener("DOMContentLoaded", function () {

    // ==================================================
    // GLOBAL VARIABLES
    // ==================================================

    let subjectChart = null;
    let difficultyChart = null;
    let yearChart = null;


    // ==================================================
    // GET HTML ELEMENTS
    // ==================================================

    const queryInput =
        document.getElementById("queryInput");

    const searchButton =
        document.getElementById("searchButton");

    const results =
        document.getElementById("results");

    const refreshAnalytics =
        document.getElementById("refreshAnalytics");

    const bookModal =
        document.getElementById("bookModal");

    const closeModal =
        document.getElementById("closeModal");


    // ==================================================
    // SEARCH BOOKS
    // ==================================================

    async function searchBooks() {

        const query =
            queryInput.value.trim();


        if (!query) {

            alert(
                "Please enter what you want to learn."
            );

            return;
        }


        results.innerHTML = `
            <div class="loading">
                🔄 Finding the best books for you...
            </div>
        `;


        try {

            const response =
                await fetch("/recommend", {

                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        query: query
                    })

                });


            if (!response.ok) {

                throw new Error(
                    "Server error: " +
                    response.status
                );

            }


            const data =
                await response.json();


            console.log(
                "Recommendation Response:",
                data
            );


            // ==========================================
            // QUERY INFORMATION
            // ==========================================

            document.getElementById(
                "difficulty"
            ).innerText =
                data.difficulty || "General";


            document.getElementById(
                "intent"
            ).innerText =
                data.intent || "General Search";


            document.getElementById(
                "practical"
            ).innerText =
                data.practical_preference
                    ? "Yes"
                    : "No";


            document.getElementById(
                "confidence"
            ).innerText =
                (
                    data.confidence * 100
                ).toFixed(1) + "%";


            // ==========================================
            // NO RESULTS
            // ==========================================

            if (
                !data.recommendations ||
                data.recommendations.length === 0
            ) {

                results.innerHTML = `

                    <div class="empty-message">

                        😕 No suitable books found.

                        <br><br>

                        Try another search.

                    </div>

                `;

                return;
            }


            // ==========================================
            // DISPLAY RECOMMENDATIONS
            // ==========================================

            results.innerHTML = "";


            data.recommendations.forEach(
                function (book, index) {

                    const card =
                        document.createElement("div");


                    card.className =
                        "book-card";


                    card.innerHTML = `

                        <div class="book-number">
                            ${index + 1}
                        </div>

                        <div class="book-icon">
                            📖
                        </div>

                        <h3>
                            ${escapeHTML(book.title)}
                        </h3>

                        <p class="author">
                            By ${escapeHTML(book.author)}
                        </p>

                        <div class="book-details">

                            <span>
                                📚
                                ${escapeHTML(book.subject)}
                            </span>

                            <span>
                                🎯
                                ${escapeHTML(book.difficulty)}
                            </span>

                            <span>
                                📅
                                ${book.year}
                            </span>

                            <span>
                                ${
                                    book.available === "Yes"
                                    ? "✅ Available"
                                    : "❌ Unavailable"
                                }
                            </span>

                        </div>

                        <div class="score">

                            Match Score:
                            ${(book.score * 100).toFixed(1)}%

                        </div>

                        <div class="reason">

                            💡
                            <strong>
                                Why Recommended:
                            </strong>

                            ${escapeHTML(book.reason)}

                        </div>

                        <button
                            class="details-btn"
                        >
                            📖 View Details
                        </button>

                    `;


                    // ======================================
                    // VIEW DETAILS BUTTON
                    // ======================================

                    const detailsButton =
                        card.querySelector(
                            ".details-btn"
                        );


                    detailsButton.addEventListener(
                        "click",
                        function () {

                            showBookDetails(book);

                        }
                    );


                    results.appendChild(card);

                }
            );


            // Scroll to recommendations

            document
                .getElementById("recommendations")
                .scrollIntoView({
                    behavior: "smooth"
                });

        }


        catch (error) {

            console.error(
                "Recommendation Error:",
                error
            );


            results.innerHTML = `

                <div class="error-message">

                    ❌ Unable to connect to the backend.

                    <br><br>

                    Make sure FastAPI is running.

                    <br><br>

                    Error:
                    ${escapeHTML(error.message)}

                </div>

            `;

        }

    }



    // ==================================================
    // ESCAPE HTML
    // ==================================================

    function escapeHTML(value) {

        if (
            value === null ||
            value === undefined
        ) {

            return "";

        }


        return String(value)

            .replace(/&/g, "&amp;")

            .replace(/</g, "&lt;")

            .replace(/>/g, "&gt;")

            .replace(/"/g, "&quot;")

            .replace(/'/g, "&#039;");

    }



    // ==================================================
    // SHOW BOOK DETAILS
    // ==================================================

    function showBookDetails(book) {

        document.getElementById(
            "modalTitle"
        ).innerText =
            book.title;


        document.getElementById(
            "modalAuthor"
        ).innerText =
            "✍️ " + book.author;


        document.getElementById(
            "modalSubject"
        ).innerText =
            "📚 " + book.subject;


        document.getElementById(
            "modalDifficulty"
        ).innerText =
            "🎯 " + book.difficulty;


        document.getElementById(
            "modalYear"
        ).innerText =
            "📅 " + book.year;


        document.getElementById(
            "modalAvailability"
        ).innerText =
            book.available === "Yes"
                ? "✅ Available"
                : "❌ Unavailable";


        document.getElementById(
            "modalDescription"
        ).innerText =
            book.description ||
            "No description available.";


        document.getElementById(
            "modalKeywords"
        ).innerText =
            book.keywords ||
            "No keywords available.";


        document.getElementById(
            "modalReason"
        ).innerText =
            book.reason ||
            "Recommended based on your search.";


        bookModal.style.display =
            "flex";

    }



    // ==================================================
    // CLOSE MODAL
    // ==================================================

    function closeBookDetails() {

        bookModal.style.display =
            "none";

    }



    // ==================================================
    // SEARCH BUTTON EVENT
    // ==================================================

    searchButton.addEventListener(
        "click",
        searchBooks
    );



    // ==================================================
    // CTRL + ENTER
    // ==================================================

    queryInput.addEventListener(
        "keydown",
        function (event) {

            if (
                event.ctrlKey &&
                event.key === "Enter"
            ) {

                searchBooks();

            }

        }
    );



    // ==================================================
    // EXAMPLE BUTTONS
    // ==================================================

    document
        .querySelectorAll(".example-btn")
        .forEach(
            function (button) {

                button.addEventListener(
                    "click",
                    function () {

                        queryInput.value =
                            this.dataset.query;


                        searchBooks();

                    }
                );

            }
        );



    // ==================================================
    // CLOSE BUTTON
    // ==================================================

    closeModal.addEventListener(
        "click",
        closeBookDetails
    );



    // ==================================================
    // CLICK OUTSIDE MODAL
    // ==================================================

    bookModal.addEventListener(
        "click",
        function (event) {

            if (
                event.target === bookModal
            ) {

                closeBookDetails();

            }

        }
    );



    // ==================================================
    // ESCAPE KEY
    // ==================================================

    document.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Escape"
            ) {

                closeBookDetails();

            }

        }
    );



    // ==================================================
    // ANALYTICS
    // ==================================================

    async function loadAnalytics() {

        try {

            const response =
                await fetch("/analytics");


            if (!response.ok) {

                throw new Error(
                    "Analytics server error: " +
                    response.status
                );

            }


            const data =
                await response.json();


            console.log(
                "Analytics Response:",
                data
            );


            // ==========================================
            // ANALYTICS CARDS
            // ==========================================

            document.getElementById(
                "totalBooks"
            ).innerText =
                data.total_books;


            document.getElementById(
                "availableBooks"
            ).innerText =
                data.available_books;


            document.getElementById(
                "unavailableBooks"
            ).innerText =
                data.unavailable_books;


            let availabilityRate = 0;


            if (
                data.total_books > 0
            ) {

                availabilityRate =
                    (
                        data.available_books /
                        data.total_books
                    ) * 100;

            }


            document.getElementById(
                "availabilityRate"
            ).innerText =
                availabilityRate.toFixed(1)
                + "%";


            // ==========================================
            // CREATE CHARTS
            // ==========================================

            createSubjectChart(
                data.books_by_subject
            );


            createDifficultyChart(
                data.books_by_difficulty
            );


            createYearChart(
                data.books_by_year
            );

        }


        catch (error) {

            console.error(
                "Analytics Error:",
                error
            );

        }

    }



    // ==================================================
    // SUBJECT CHART
    // ==================================================

    function createSubjectChart(data) {

        const labels =
            Object.keys(data);


        const values =
            Object.values(data);


        const canvas =
            document.getElementById(
                "subjectChart"
            );


        if (!canvas) {

            console.error(
                "subjectChart canvas not found."
            );

            return;
        }


        if (subjectChart) {

            subjectChart.destroy();

        }


        subjectChart =
            new Chart(
                canvas,
                {

                    type: "bar",

                    data: {

                        labels: labels,

                        datasets: [

                            {

                                label:
                                    "Number of Books",

                                data:
                                    values

                            }

                        ]

                    },

                    options: {

                        responsive: true,

                        maintainAspectRatio:
                            false,

                        plugins: {

                            legend: {

                                display: false

                            }

                        },

                        scales: {

                            y: {

                                beginAtZero:
                                    true,

                                ticks: {

                                    stepSize: 1

                                }

                            }

                        }

                    }

                }
            );

    }



    // ==================================================
    // DIFFICULTY CHART
    // ==================================================

    function createDifficultyChart(data) {

        const labels =
            Object.keys(data);


        const values =
            Object.values(data);


        const canvas =
            document.getElementById(
                "difficultyChart"
            );


        if (!canvas) {

            console.error(
                "difficultyChart canvas not found."
            );

            return;
        }


        if (difficultyChart) {

            difficultyChart.destroy();

        }


        difficultyChart =
            new Chart(
                canvas,
                {

                    type: "doughnut",

                    data: {

                        labels: labels,

                        datasets: [

                            {

                                label:
                                    "Books",

                                data:
                                    values

                            }

                        ]

                    },

                    options: {

                        responsive: true,

                        maintainAspectRatio:
                            false,

                        plugins: {

                            legend: {

                                position:
                                    "bottom"

                            }

                        }

                    }

                }
            );

    }



    // ==================================================
    // YEAR CHART
    // ==================================================

    function createYearChart(data) {

        const labels =
            Object.keys(data);


        const values =
            Object.values(data);


        const canvas =
            document.getElementById(
                "yearChart"
            );


        if (!canvas) {

            console.error(
                "yearChart canvas not found."
            );

            return;
        }


        if (yearChart) {

            yearChart.destroy();

        }


        yearChart =
            new Chart(
                canvas,
                {

                    type: "line",

                    data: {

                        labels: labels,

                        datasets: [

                            {

                                label:
                                    "Books Published",

                                data:
                                    values,

                                tension:
                                    0.3,

                                fill:
                                    false

                            }

                        ]

                    },

                    options: {

                        responsive: true,

                        maintainAspectRatio:
                            false,

                        scales: {

                            y: {

                                beginAtZero:
                                    true,

                                ticks: {

                                    stepSize: 1

                                }

                            }

                        }

                    }

                }
            );

    }



    // ==================================================
    // REFRESH ANALYTICS
    // ==================================================

    refreshAnalytics.addEventListener(
        "click",
        loadAnalytics
    );



    // ==================================================
    // INITIAL ANALYTICS LOAD
    // ==================================================

    loadAnalytics();

});