document.addEventListener("DOMContentLoaded", function () {
    // Confirm before deleting important information.
    document.querySelectorAll("form[data-confirm]").forEach(function (form) {
        form.addEventListener("submit", function (event) {
            const message = form.getAttribute("data-confirm");

            if (!window.confirm(message)) {
                event.preventDefault();
            }
        });
    });

    // Draw numeric health metrics using Chart.js.
    const dataElement = document.getElementById("metrics-data");
    const canvas = document.getElementById("metrics-chart");

    if (!dataElement || !canvas || typeof Chart === "undefined") {
        return;
    }

    let records;

    try {
        records = JSON.parse(dataElement.textContent);
    } catch (error) {
        console.error("Could not read chart data.", error);
        return;
    }

    const types = ["Weight", "Blood Pressure", "Blood Sugar"];
    const datasets = [];

    types.forEach(function (type) {
        const points = records
            .filter(function (item) {
                return item.type === type && item.value !== "";
            })
            .map(function (item) {
                return {
                    x: item.date,
                    y: Number(item.value)
                };
            })
            .filter(function (point) {
                return Number.isFinite(point.y);
            });

        if (points.length > 0) {
            datasets.push({
                label: type,
                data: points,
                tension: 0.25
            });
        }
    });

    if (datasets.length === 0) {
        const message = document.createElement("p");
        message.className = "muted";
        message.textContent =
            "No numeric measurements to chart yet. Add a numeric value to see a chart.";
        canvas.parentElement.appendChild(message);
        canvas.style.display = "none";
        return;
    }

    new Chart(canvas, {
        type: "line",
        data: {
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            parsing: false,
            scales: {
                x: {
                    type: "category",
                    labels: records.map(function (item) {
                        return item.date;
                    })
                },
                y: {
                    beginAtZero: false
                }
            },
            plugins: {
                legend: {
                    position: "bottom"
                }
            }
        }
    });
});