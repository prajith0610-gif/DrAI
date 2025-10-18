// Leaflet map for doctors & ambulances
var map = L.map('map').setView([12.9716, 77.5946], 12);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

// Add doctor markers
var doctors = document.querySelectorAll(".doctors li");
doctors.forEach(function(doc) {
    // For simplicity, you can add coordinates in JS if needed
});

// Add ambulance markers (example)
var ambulances = document.querySelectorAll(".ambulance li");
ambulances.forEach(function(amb) {
    // Example locations
    var lat = 12.9720;
    var lon = 77.6200;
    L.marker([lat, lon]).addTo(map).bindPopup(amb.textContent);
});
