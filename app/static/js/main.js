// Main JavaScript file for handling user interactions

let selectedBooking = null;
let selectedSeats = [];

function processPrompt() {
    const prompt = document.getElementById('userPrompt').value;
    if (!prompt) {
        showError('Please enter your travel requirements');
        return;
    }

    showLoading();

    // Send prompt to backend
    fetch('/process_prompt', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt: prompt })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            displayResults(data);
        } else {
            showError(data.message);
        }
    })
    .catch(error => {
        showError('An error occurred while processing your request.');
        console.error('Error:', error);
    })
    .finally(() => {
        hideLoading();
    });
}

function displayResults(data) {
    const responseArea = document.getElementById('responseArea');
    responseArea.innerHTML = '';

    if (data.type === 'hotel') {
        displayHotelResults(data.results);
    } else if (data.type === 'transport') {
        displayTransportResults(data.results);
    }
}

function displayHotelResults(hotels) {
    const responseArea = document.getElementById('responseArea');
    let html = '<div class="row">';

    hotels.forEach((hotel, index) => {
        html += `
            <div class="col-md-6 mb-4">
                <div class="card hotel-card">
                    <img src="${hotel.images[0]}" class="card-img-top" alt="${hotel.name}">
                    <div class="price-tag">₹${hotel.price.amount}</div>
                    <div class="card-body">
                        <h5 class="card-title">${hotel.name}</h5>
                        <div class="rating-stars">
                            ${generateStars(hotel.rating)}
                        </div>
                        <p class="card-text">
                            <i class="fas fa-map-marker-alt"></i> ${hotel.location.address}
                        </p>
                        <div class="amenities-list">
                            ${generateAmenityBadges(hotel.amenities)}
                        </div>
                        <button class="btn btn-primary mt-3" onclick="showHotelBooking('${hotel.source}', '${hotel.hotel_id}')">
                            Book Now
                        </button>
                    </div>
                </div>
            </div>
        `;
    });

    html += '</div>';
    responseArea.innerHTML = html;
}

function displayTransportResults(options) {
    const responseArea = document.getElementById('responseArea');
    let html = '<div class="row">';

    options.forEach((option, index) => {
        html += `
            <div class="col-12 mb-4">
                <div class="card transport-card">
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-3">
                                <h5 class="card-title">${option.operator_name}</h5>
                                <p class="text-muted">${option.bus_type}</p>
                            </div>
                            <div class="col-md-3">
                                <div class="text-center">
                                    <strong>${formatTime(option.departure_time)}</strong>
                                    <div class="text-muted">Departure</div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="text-center">
                                    <strong>${formatTime(option.arrival_time)}</strong>
                                    <div class="text-muted">Arrival</div>
                                </div>
                            </div>
                            <div class="col-md-3 text-end">
                                <h5 class="text-primary">₹${option.fare}</h5>
                                <button class="btn btn-primary" onclick="showTransportBooking('${option.bus_id}')">
                                    Select Seats
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });

    html += '</div>';
    responseArea.innerHTML = html;
}

function showHotelBooking(source, hotelId) {
    selectedBooking = { type: 'hotel', source, hotelId };
    const modal = new bootstrap.Modal(document.getElementById('hotelBookingModal'));
    modal.show();
}

function showTransportBooking(busId) {
    selectedBooking = { type: 'transport', busId };
    
    // Get seat layout
    fetch(`/get_seat_layout?bus_id=${busId}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                displaySeatLayout(data.layout);
                const modal = new bootstrap.Modal(document.getElementById('transportBookingModal'));
                modal.show();
            } else {
                showError('Unable to load seat layout');
            }
        })
        .catch(error => {
            showError('Error loading seat layout');
            console.error('Error:', error);
        });
}

function displaySeatLayout(layout) {
    const seatLayoutDiv = document.getElementById('seatLayout');
    let html = '<div class="seat-layout">';

    layout.forEach((row, rowIndex) => {
        html += '<div class="row">';
        row.forEach((seat, seatIndex) => {
            const seatClass = seat.available ? 'available' : 'booked';
            const seatNumber = `${rowIndex + 1}${String.fromCharCode(65 + seatIndex)}`;
            html += `
                <div class="seat ${seatClass}" 
                    onclick="toggleSeat('${seatNumber}', ${seat.available})"
                    data-seat="${seatNumber}">
                    ${seatNumber}
                </div>
            `;
        });
        html += '</div>';
    });

    html += '</div>';
    seatLayoutDiv.innerHTML = html;
}

function toggleSeat(seatNumber, available) {
    if (!available) return;

    const seatElement = document.querySelector(`[data-seat="${seatNumber}"]`);
    const seatIndex = selectedSeats.indexOf(seatNumber);

    if (seatIndex === -1) {
        selectedSeats.push(seatNumber);
        seatElement.classList.add('selected');
    } else {
        selectedSeats.splice(seatIndex, 1);
        seatElement.classList.remove('selected');
    }

    updateBookingSummary();
}

function updateBookingSummary() {
    const summaryDiv = document.getElementById('bookingSummary');
    if (selectedSeats.length > 0) {
        summaryDiv.innerHTML = `
            <div class="booking-summary">
                <h6>Selected Seats: ${selectedSeats.join(', ')}</h6>
                <p>Total Amount: ₹${calculateTotalAmount()}</p>
            </div>
        `;
    } else {
        summaryDiv.innerHTML = '';
    }
}

function confirmHotelBooking() {
    const form = document.getElementById('hotelBookingForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const formData = new FormData(form);
    const bookingData = {
        type: 'hotel',
        source: selectedBooking.source,
        hotel_id: selectedBooking.hotelId,
        check_in: formData.get('check_in'),
        check_out: formData.get('check_out'),
        guests: formData.get('guests'),
        rooms: formData.get('rooms')
    };

    initiateBooking(bookingData);
}

function confirmTransportBooking() {
    if (selectedSeats.length === 0) {
        showError('Please select at least one seat');
        return;
    }

    const form = document.getElementById('transportBookingForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const formData = new FormData(form);
    const bookingData = {
        type: 'transport',
        bus_id: selectedBooking.busId,
        seats: selectedSeats,
        passenger_name: formData.get('passenger_name'),
        age: formData.get('age'),
        gender: formData.get('gender'),
        phone: formData.get('phone')
    };

    initiateBooking(bookingData);
}

function initiateBooking(bookingData) {
    fetch('/initiate_booking', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(bookingData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Redirect to payment URL
            window.location.href = data.payment_url;
        } else {
            showError(data.message);
        }
    })
    .catch(error => {
        showError('Error initiating booking');
        console.error('Error:', error);
    });
}

// Utility Functions
function generateStars(rating) {
    const fullStars = Math.floor(rating);
    const halfStar = rating % 1 >= 0.5;
    let stars = '';

    for (let i = 0; i < fullStars; i++) {
        stars += '<i class="fas fa-star"></i>';
    }
    if (halfStar) {
        stars += '<i class="fas fa-star-half-alt"></i>';
    }
    return stars;
}

function generateAmenityBadges(amenities) {
    return amenities.slice(0, 4).map(amenity => 
        `<span class="amenity-badge"><i class="fas fa-check"></i> ${amenity}</span>`
    ).join('');
}

function formatTime(timeString) {
    return new Date(timeString).toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

function showLoading() {
    const responseArea = document.getElementById('responseArea');
    responseArea.innerHTML = `
        <div class="loading-spinner">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>
    `;
}

function hideLoading() {
    // Loading will be replaced by results
}

function showError(message) {
    const responseArea = document.getElementById('responseArea');
    responseArea.innerHTML = `
        <div class="error-message">
            <i class="fas fa-exclamation-circle"></i> ${message}
        </div>
    `;
}

function calculateTotalAmount() {
    // Implement price calculation based on selected seats
    return selectedSeats.length * 800; // Example price
}