document.addEventListener('DOMContentLoaded', function() {
    // MOTOR_ID is set by Flask in device_detail.html
    if (typeof MOTOR_ID === 'undefined') {
        console.error("MOTOR_ID not defined. Cannot load detail page.");
        return;
    }

    const elements = {
        motorName: document.getElementById('motor-name'),
        healthBadge: document.getElementById('health-status-badge'),
        timestamp: document.getElementById('timestamp'),
        tempValue: document.getElementById('temp-value'),
        vibValue: document.getElementById('vib-value'),
        soundValue: document.getElementById('sound-value'),
        motorType: document.getElementById('motor-type'),
        ratedPower: document.getElementById('rated-power'),
        installDate: document.getElementById('install-date'),
        chartCanvas: document.getElementById('temperatureChart').getContext('2d'),
    };
    
    let tempChart; // To hold the Chart.js instance

    // --- 1. Real-time WebSocket Setup ---
    // Connect to the Socket.IO server running on Flask
    const socket = io();

    // Listener for new sensor reading broadcasts
    socket.on('new_reading', function(data) {
        // ONLY update if the reading is for the motor currently being viewed
        if (data.motor_id === MOTOR_ID) {
            updateReadingDisplay(data);
        }
    });

    // Helper function to update the DOM with new data
    function updateReadingDisplay(reading) {
        elements.timestamp.textContent = reading.timestamp.split(' ')[1]; // Only show time for simplicity
        elements.tempValue.textContent = `${reading.temperature_celsius} °C`;
        elements.vibValue.textContent = `${reading.vibration_mm_s} mm/s`;
        elements.soundValue.textContent = `${reading.sound_db} dB`;
        
        // Update Health Status Badge based on temperature threshold (Critical > 80)
        let status = 'Normal';
        if (reading.temperature_celsius >= 80) {
            status = 'Critical';
        } else if (reading.temperature_celsius >= 70) {
            status = 'Warning';
        }

        elements.healthBadge.textContent = status;
        elements.healthBadge.className = `status-badge ${status}`;
    }


    // --- 2. Initial Data Fetching ---

    // A. Fetch Motor Details and Latest Reading
    fetch(`/api/motors/${MOTOR_ID}/detail`) // We'll modify the backend API slightly for this fetch
        .then(response => response.json())
        .then(data => {
            if (data.length > 0) {
                const motor = data[0]; // Assuming the API returns a list with one motor

                // Populate Static Specs
                elements.motorName.textContent = motor.motor_name;
                elements.motorType.textContent = motor.motor_type;
                elements.ratedPower.textContent = motor.rated_power_kw;
                elements.installDate.textContent = motor.installation_date || 'N/A';

                // Initial Latest Reading Display
                if (motor.latest_reading) {
                    updateReadingDisplay(motor.latest_reading);
                }
            }
        })
        .catch(error => console.error('Error fetching motor details:', error));


    // B. Fetch Historical Data for Chart
    fetch(`/api/sensors/${MOTOR_ID}/history`)
        .then(response => response.json())
        .then(data => {
            tempChart = new Chart(elements.chartCanvas, {
                type: 'line',
                data: {
                    labels: data.timestamps,
                    datasets: [{
                        label: 'Temperature (°C) - Last 24 Hrs (Mock Data)',
                        data: data.temperature,
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1,
                        fill: false
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: false,
                            title: {
                                display: true,
                                text: 'Temperature (°C)'
                            }
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Error fetching history:', error));

    // Fix a temporary issue from Step 4 (The API was designed for zone_id, not single motor detail)
    // We will add a temporary detail route in the backend now to make this fetch work correctly.
});