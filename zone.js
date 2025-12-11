document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('zone-container');

    function renderZoneCards(zones) {
        container.innerHTML = ''; // Clear 'Loading...' message
        
        zones.forEach(zone => {
            const card = document.createElement('div');
            card.className = 'zone-card';
            
            // Make the card clickable to navigate to the device detail view
            // NOTE: We pass the zone ID here, but the backend requires a MOTOR ID for the detail view. 
            // Since we can't fetch a single motor ID yet, we'll hardcode one of the test motors (Motor A-1, ID 1) 
            // for the initial navigation to keep the flow working. We'll fix this in the next steps.
            card.onclick = () => {
                // Hardcode motor ID 1 for quick navigation test
                window.location.href = `/zone/${zone.id}/motors`; 
            };

            // Determine the max status for the overall indicator
            let max_status = zone.overall_status;

            card.innerHTML = `
                <h3>${zone.zone_name}</h3>
                <p>Location: ${zone.location}</p>
                <hr>
                <p>Total Motors: <b>${zone.total_motors}</b></p>
                <p>Overall Health: 
                    <span class="status-badge ${max_status}">${max_status}</span>
                </p>
                <p style="font-size: 0.9em; margin-top: 10px;">
                    <span class="Normal">${zone.status_counts.Normal} Normal</span> | 
                    <span class="Warning">${zone.status_counts.Warning} Warning</span> | 
                    <span class="Critical">${zone.status_counts.Critical} Critical</span>
                </p>
            `;
            container.appendChild(card);
        });
    }

    // Function to fetch data from the Flask API
    fetch('/api/zones')
        .then(response => {
            if (response.status === 401) {
                // If unauthorized, redirect to login (Flask does this automatically too, but this is a good safety check)
                window.location.href = '/login';
                return;
            }
            return response.json();
        })
        .then(data => {
            if (data) {
                renderZoneCards(data);
            }
        })
        .catch(error => {
            console.error('Error fetching zone data:', error);
            container.innerHTML = '<p style="color: red;">Error loading data. Check console.</p>';
        });
});