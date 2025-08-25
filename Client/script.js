document.getElementById('weatherForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const lat = document.getElementById('lat').value;
    const lon = document.getElementById('lon').value;
    const resultsDiv = document.getElementById('weatherResults');
    resultsDiv.innerHTML = 'Loading weather data...';

    try {
        const response = await fetch(`http://localhost:5000/weather-report?lat=${lat}&lon=${lon}`);
        if (!response.ok) throw new Error(`Error: ${response.statusText}`);
        const data = await response.json();

        if (!data.length) {
            resultsDiv.innerHTML = '<p>No weather data available.</p>';
            return;
        }

        // Create table of results
        let html = '<table><thead><tr><th>Timestamp</th><th>Temperature (°C)</th><th>Humidity (%)</th></tr></thead><tbody>';
        data.forEach(row => {
            html += `<tr><td>${row.timestamp}</td><td>${row.temperature}</td><td>${row.humidity}</td></tr>`;
        });
        html += '</tbody></table>';
        resultsDiv.innerHTML = html;

    } catch (error) {
        resultsDiv.innerHTML = `<p>${error.message}</p>`;
    }
});

document.getElementById('downloadExcel').addEventListener('click', () => {
    // Get lat/lon values for Excel request
    const lat = document.getElementById('lat').value;
    const lon = document.getElementById('lon').value;
    // Triggers download of Excel file directly from backend endpoint
    window.location.href = `http://localhost:5000/export/excel?lat=${lat}&lon=${lon}`;
});

document.getElementById('downloadPDF').addEventListener('click', () => {
    // Get lat/lon values for PDF request
    const lat = document.getElementById('lat').value;
    const lon = document.getElementById('lon').value;
    window.location.href = `http://localhost:5000/export/pdf?lat=${lat}&lon=${lon}`;
});
