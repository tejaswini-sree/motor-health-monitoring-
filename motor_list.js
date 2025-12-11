document.addEventListener('DOMContentLoaded', function() {
    // ZONE_ID is set by Flask in motor_list.html
    const container = document.getElementById('motor-list-container');
    document.getElementById('zone-id-display').textContent = ZONE_ID;
    
    // Function to fetch and display the motor list
    function fetchMotorList() {
        container.innerHTML = '<p id="loading-message">Loading Motors...</p>'; // Show loading

        fetch(`/api/motors/${ZONE_ID}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(motors => {
                container.innerHTML = ''; // Clear loading message

                if (motors.length === 0) {
                    container.innerHTML = '<p>No motors found in this zone.</p>';
                    return;
                }

                motors.forEach(motor => {
                    const card = document.createElement('div');
                    card.className = 'motor-card';
                    
                    // Set the link to the detail page on click
                    card.onclick = () => {
                        window.location.href = `/device/${motor.id}`;
                    };

                    // Health status badge setup
                    const status = motor.health_status || 'Normal';
                    const statusBadge = `<span class="status-badge ${status}">${status}</span>`;

                    card.innerHTML = `
                        <h3>${motor.motor_name} (ID: ${motor.id}) ${statusBadge}</h3>
                        <p>Type: ${motor.motor_type}</p>
                        <p>Power: ${motor.rated_power_kw} kW</p>
                        <p>Temp: ${motor.latest_reading.temperature_celsius.toFixed(2)} °C</p>
                        <p>Vib: ${motor.latest_reading.vibration_mm_s.toFixed(2)} mm/s</p>
                    `;
                    container.appendChild(card);
                });
            })
            .catch(error => {
                console.error('Error fetching motor list:', error);
                container.innerHTML = `<p style="color:red;">Error loading motors: ${error.message}</p>`;
            });
    }

    fetchMotorList();
});