// Estado Global
let movies = [];
let seats = {};
let selectedMovie = null;
let selectedTime = null;
let selectedSeats = [];
let isAdmin = false;
let currentSlide = 0;
let currentUser = null;
let selectedCollectible = null;

const PRICE_PER_SEAT = 12000;
const COLLECTIBLE_PRICES = {
    '': 0,
    'Vaso Coleccionable': 8000,
    'Poster Exclusivo': 15000,
    'Combo Premium': 25000,
    'Figura Coleccionable': 35000
};

// Posters de ejemplo (URLs de imágenes)
const moviePosters = [
    'https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=400&h=600&fit=crop',
    'https://images.unsplash.com/photo-1594908900066-3f47337549d8?w=400&h=600&fit=crop',
    'https://images.unsplash.com/photo-1635805737707-575885ab0820?w=400&h=600&fit=crop',
    'https://images.unsplash.com/photo-1598899134739-24c46f58b8c0?w=400&h=600&fit=crop',
    'https://images.unsplash.com/photo-1509347528160-9a9e33742cdb?w=400&h=600&fit=crop'
];

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initAuth();
    checkSession();
    loadMovies();
    initSlider();
    initAdminPanel();
});

// NAVEGACIÓN
function initNavigation() {
    const navBtns = document.querySelectorAll('.nav-btn');
    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const view = btn.dataset.view;
            if (view) {
                switchView(view);
                navBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                if (view === 'profile') {
                    loadTickets();
                } else if (view === 'admin') {
                    loadAdminData();
                }
            }
        });
    });
}

// AUTENTICACIÓN
function initAuth() {
    const loginBtn = document.getElementById('loginBtn');
    const loginModal = document.getElementById('loginModal');
    const registerModal = document.getElementById('registerModal');
    const closeLogin = document.getElementById('closeLogin');
    const closeRegister = document.getElementById('closeRegister');
    const showRegister = document.getElementById('showRegister');
    const showLogin = document.getElementById('showLogin');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');

    // Abrir modal de login
    loginBtn.addEventListener('click', () => {
        if (currentUser) {
            // Si ya está logueado, cerrar sesión
            logout();
        } else {
            loginModal.classList.add('active');
        }
    });

    // Cerrar modales
    closeLogin.addEventListener('click', () => {
        loginModal.classList.remove('active');
    });

    closeRegister.addEventListener('click', () => {
        registerModal.classList.remove('active');
    });

    // Cambiar entre login y registro
    showRegister.addEventListener('click', (e) => {
        e.preventDefault();
        loginModal.classList.remove('active');
        registerModal.classList.add('active');
    });

    showLogin.addEventListener('click', (e) => {
        e.preventDefault();
        registerModal.classList.remove('active');
        loginModal.classList.add('active');
    });

    // Cerrar modal al hacer clic fuera
    window.addEventListener('click', (e) => {
        if (e.target === loginModal) {
            loginModal.classList.remove('active');
        }
        if (e.target === registerModal) {
            registerModal.classList.remove('active');
        }
    });

    // Formulario de login
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const correo = document.getElementById('loginEmail').value;
        const contraseña = document.getElementById('loginPassword').value;

        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ correo, contraseña })
            });

            const data = await response.json();

            if (data.success) {
                alert(`✅ ${data.mensaje}`);
                currentUser = data.usuario;
                updateUserUI();
                loginModal.classList.remove('active');
                loginForm.reset();
            } else {
                alert('❌ ' + data.error);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('❌ Error al iniciar sesión');
        }
    });

    // Formulario de registro
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const nombre = document.getElementById('registerName').value;
        const correo = document.getElementById('registerEmail').value;
        const contraseña = document.getElementById('registerPassword').value;

        try {
            const response = await fetch('/api/auth/registro', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ nombre, correo, contraseña })
            });

            const data = await response.json();

            if (data.success) {
                alert(`✅ ${data.mensaje}`);
                currentUser = data.usuario;
                updateUserUI();
                registerModal.classList.remove('active');
                registerForm.reset();
            } else {
                alert('❌ ' + data.error);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('❌ Error al registrarse');
        }
    });
}

async function checkSession() {
    try {
        const response = await fetch('/api/auth/session');
        const data = await response.json();

        if (data.logged_in) {
            currentUser = data.usuario;
            updateUserUI();
        }
    } catch (error) {
        console.error('Error al verificar sesión:', error);
    }
}

async function logout() {
    try {
        const response = await fetch('/api/auth/logout', { method: 'POST' });
        const data = await response.json();

        if (data.success) {
            alert('✅ Sesión cerrada');
            currentUser = null;
            updateUserUI();
            switchView('home');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

function updateUserUI() {
    const loginBtn = document.getElementById('loginBtn');
    const userNameDisplay = document.getElementById('userNameDisplay');
    const adminBtn = document.getElementById('adminBtn');

    if (currentUser) {
        userNameDisplay.textContent = currentUser.nombre;
        loginBtn.innerHTML = `
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                <polyline points="16 17 21 12 16 7"></polyline>
                <line x1="21" y1="12" x2="9" y2="12"></line>
            </svg>
            <span id="userNameDisplay">${currentUser.nombre}</span>
        `;

        if (currentUser.es_admin) {
            adminBtn.style.display = 'flex';
            isAdmin = true;
        } else {
            adminBtn.style.display = 'none';
            isAdmin = false;
        }
    } else {
        userNameDisplay.textContent = '';
        loginBtn.innerHTML = `
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"></path>
                <polyline points="10 17 15 12 10 7"></polyline>
                <line x1="15" y1="12" x2="3" y2="12"></line>
            </svg>
            <span id="userNameDisplay"></span>
        `;
        adminBtn.style.display = 'none';
        isAdmin = false;
    }
}

function switchView(viewName) {
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.getElementById(`${viewName}View`).classList.add('active');
}

// CARGAR PELÍCULAS
async function loadMovies() {
    try {
        const response = await fetch('/api/cartelera');
        movies = await response.json();
        renderSlider();
        renderMoviesGrid();
    } catch (error) {
        console.error('Error al cargar películas:', error);
    }
}

// SLIDER
function initSlider() {
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');

    prevBtn.addEventListener('click', () => {
        currentSlide = (currentSlide - 1 + Math.min(3, movies.length)) % Math.min(3, movies.length);
        updateSlider();
    });

    nextBtn.addEventListener('click', () => {
        currentSlide = (currentSlide + 1) % Math.min(3, movies.length);
        updateSlider();
    });

    // Auto-slide
    setInterval(() => {
        if (movies.length > 0) {
            currentSlide = (currentSlide + 1) % Math.min(3, movies.length);
            updateSlider();
        }
    }, 4000);
}

function renderSlider() {
    const sliderTrack = document.getElementById('sliderTrack');
    sliderTrack.innerHTML = '';

    movies.slice(0, 3).forEach((movie, idx) => {
        const slide = document.createElement('div');
        slide.className = 'slide';
        slide.innerHTML = `
            <img src="${moviePosters[idx % moviePosters.length]}" alt="${movie.titulo}">
            <div class="slide-overlay">
                <div class="slide-content">
                    <div class="slide-inner">
                        <span class="badge-estreno">ESTRENO</span>
                        <h2 class="slide-title">${movie.titulo}</h2>
                        <p class="slide-info">${movie.genero} • ${movie.duracion} min • +${movie.clasificacion}</p>
                        <button class="slide-btn" onclick="viewMovieDetails(${idx})">VER HORARIOS</button>
                    </div>
                </div>
            </div>
        `;
        sliderTrack.appendChild(slide);
    });
}

function updateSlider() {
    const sliderTrack = document.getElementById('sliderTrack');
    sliderTrack.style.transform = `translateX(-${currentSlide * 100}%)`;
}

// GRID DE PELÍCULAS
function renderMoviesGrid() {
    const grid = document.getElementById('moviesGrid');
    grid.innerHTML = '';

    movies.forEach((movie, idx) => {
        const card = document.createElement('div');
        card.className = 'movie-card';
        card.onclick = () => viewMovieDetails(idx);
        card.innerHTML = `
            <div class="movie-poster">
                <img src="${moviePosters[idx % moviePosters.length]}" alt="${movie.titulo}">
                <div class="movie-overlay">
                    <span>VER HORARIOS →</span>
                </div>
            </div>
            <h3 class="movie-title">${movie.titulo}</h3>
            <p class="movie-genre">${movie.genero}</p>
            <p class="movie-rating">+${movie.clasificacion} años</p>
        `;
        grid.appendChild(card);
    });
}

// DETALLES DE PELÍCULA
function viewMovieDetails(index) {
    selectedMovie = movies[index];
    renderMovieDetails();
    switchView('details');
}

function renderMovieDetails() {
    const movieIdx = movies.indexOf(selectedMovie);
    const heroDiv = document.getElementById('movieHero');
    heroDiv.innerHTML = `
        <div class="hero-bg">
            <img src="${moviePosters[movieIdx % moviePosters.length]}" alt="${selectedMovie.titulo}">
        </div>
        <div class="hero-overlay"></div>
    `;

    const detailsDiv = document.getElementById('movieDetails');
    detailsDiv.innerHTML = `
        <img src="${moviePosters[movieIdx % moviePosters.length]}" alt="${selectedMovie.titulo}" class="details-poster">
        <div class="details-info">
            <button class="back-btn" onclick="switchView('home')">
                <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <polyline points="15 18 9 12 15 6"></polyline>
                </svg>
                Volver a cartelera
            </button>
            <h1 class="details-title">${selectedMovie.titulo}</h1>
            <div class="details-meta">
                <div class="meta-item">
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <rect x="2" y="7" width="20" height="15" rx="2" ry="2"></rect>
                        <polyline points="7 2 12 7 17 2"></polyline>
                    </svg>
                    ${selectedMovie.genero}
                </div>
                <div class="meta-item">
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <circle cx="12" cy="12" r="10"></circle>
                        <polyline points="12 6 12 12 16 14"></polyline>
                    </svg>
                    ${selectedMovie.duracion} min
                </div>
                <div class="meta-item">
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                        <circle cx="12" cy="7" r="4"></circle>
                    </svg>
                    +${selectedMovie.clasificacion} años
                </div>
            </div>
            <p class="details-description">
                Una experiencia cinematográfica épica que te llevará a través de un viaje inolvidable.
                No te pierdas este estreno que está conquistando la taquilla mundial.
            </p>
            <h2 class="schedule-title">Horarios Disponibles</h2>
            <div class="schedule-buttons">
                ${selectedMovie.horarios.map(horario => `
                    <button class="schedule-btn" onclick="selectTime('${horario}')">${horario}</button>
                `).join('')}
            </div>
        </div>
    `;
}

// SELECCIÓN DE ASIENTOS
async function loadSeats(pelicula, horario) {
    try {
        const response = await fetch(`/api/asientos/${encodeURIComponent(pelicula)}/${encodeURIComponent(horario)}`);
        seats = await response.json();
    } catch (error) {
        console.error('Error al cargar asientos:', error);
    }
}

function selectTime(time) {
    selectedTime = time;
    selectedSeats = [];
    // Cargar asientos específicos para esta película y horario
    loadSeats(selectedMovie.titulo, time).then(() => {
        loadRecommendation(selectedMovie.titulo, time).then(() => {
            renderSeats();
            switchView('seats');
        });
    });

    document.getElementById('backToDetails').onclick = () => {
        renderMovieDetails();
        switchView('details');
    };
}

async function loadRecommendation(pelicula, horario) {
    try {
        const response = await fetch(`/api/recomendacion/${encodeURIComponent(pelicula)}/${encodeURIComponent(horario)}`);
        const data = await response.json();

        // Mostrar recomendación en el selector de asientos
        const seatsMain = document.querySelector('.seats-main');
        const existingRec = document.querySelector('.recommendation-box');
        if (existingRec) existingRec.remove();

        const recBox = document.createElement('div');
        recBox.className = `recommendation-box ${data.nivel}`;
        recBox.innerHTML = `
            <div class="recommendation-header">
                <span class="recommendation-icon">${data.nivel === 'alta' ? '⚠️' : data.nivel === 'baja' ? '✅' : 'ℹ️'}</span>
                <span class="recommendation-title">Recomendación de Ocupación</span>
            </div>
            <p class="recommendation-message">${data.mensaje}</p>
            <div class="recommendation-stats">
                <span>Ocupación: <strong>${data.ocupacion}%</strong></span>
                <span>Disponibles: <strong>${data.asientos_disponibles}/${data.asientos_totales}</strong></span>
            </div>
        `;

        const screenArea = document.querySelector('.screen-area');
        screenArea.parentNode.insertBefore(recBox, screenArea);

    } catch (error) {
        console.error('Error al cargar recomendación:', error);
    }
}

function renderSeats() {
    document.getElementById('seatsMovieTitle').textContent = selectedMovie.titulo;
    document.getElementById('seatsMovieTime').textContent = `Horario: ${selectedTime}`;

    const grid = document.getElementById('seatsGrid');
    grid.innerHTML = '';

    for (let row = 0; row < 10; row++) {
        const letter = String.fromCharCode(65 + row);
        const rowDiv = document.createElement('div');
        rowDiv.className = 'seat-row';

        rowDiv.innerHTML = `<span class="row-label">${letter}</span>`;

        const seatsDiv = document.createElement('div');
        seatsDiv.className = 'row-seats';

        for (let col = 1; col <= 10; col++) {
            const seatId = `${letter}${col}`;
            const isOccupied = seats[seatId];
            const isSelected = selectedSeats.includes(seatId);

            const seatBtn = document.createElement('button');
            seatBtn.className = `seat ${isOccupied ? 'occupied' : isSelected ? 'selected' : 'available'}`;
            seatBtn.textContent = isOccupied ? '✕' : col;
            seatBtn.disabled = isOccupied;

            if (!isOccupied) {
                seatBtn.onclick = () => toggleSeat(seatId);
            }

            seatsDiv.appendChild(seatBtn);
        }

        rowDiv.appendChild(seatsDiv);
        grid.appendChild(rowDiv);
    }

    // Configurar el selector de coleccionables
    const collectibleSelect = document.getElementById('collectibleSelect');
    if (collectibleSelect && !collectibleSelect.dataset.initialized) {
        collectibleSelect.addEventListener('change', (e) => {
            selectedCollectible = e.target.value || null;
            updateSummary();
        });
        collectibleSelect.dataset.initialized = 'true';
    }

    updateSummary();
}

function toggleSeat(seatId) {
    if (selectedSeats.includes(seatId)) {
        selectedSeats = selectedSeats.filter(s => s !== seatId);
    } else {
        selectedSeats.push(seatId);
    }
    renderSeats();
}

function updateSummary() {
    document.getElementById('summaryMovie').textContent = selectedMovie.titulo;
    document.getElementById('summaryTime').textContent = selectedTime;
    document.getElementById('summarySeats').textContent = selectedSeats.length > 0 ? selectedSeats.join(', ') : 'Ninguno';

    const ticketsTotal = selectedSeats.length * PRICE_PER_SEAT;
    const collectibleTotal = selectedCollectible ? COLLECTIBLE_PRICES[selectedCollectible] : 0;
    const total = ticketsTotal + collectibleTotal;

    document.getElementById('ticketsPrice').textContent = `${ticketsTotal.toLocaleString()}`;
    document.getElementById('collectiblePrice').textContent = `${collectibleTotal.toLocaleString()}`;
    document.getElementById('total').textContent = `${total.toLocaleString()}`;

    const buyBtn = document.getElementById('buyBtn');
    buyBtn.disabled = selectedSeats.length === 0;
    buyBtn.onclick = buyTickets;
}

// COMPRAR BOLETOS
async function buyTickets() {
    if (!currentUser) {
        alert('⚠️ Debes iniciar sesión para comprar boletos');
        document.getElementById('loginModal').classList.add('active');
        return;
    }

    try {
        const response = await fetch('/api/comprar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                pelicula: selectedMovie.titulo,
                horario: selectedTime,
                asientos: selectedSeats,
                coleccionable: selectedCollectible  // Incluir coleccionable
            })
        });

        const data = await response.json();

        if (data.success) {
            const collectibleMsg = selectedCollectible ? `\nColeccionable: ${selectedCollectible}` : '';
            alert(`✅ ¡Compra exitosa!\nCódigo: ${data.codigo}${collectibleMsg}`);
            selectedSeats = [];
            selectedCollectible = null;
            document.getElementById('collectibleSelect').value = '';
            // Recargar asientos de esta función específica
            await loadSeats(selectedMovie.titulo, selectedTime);
            switchView('profile');
            loadTickets();
        } else {
            alert('❌ Error: ' + (data.error || 'No se pudo procesar la compra'));
        }
    } catch (error) {
        console.error('Error al comprar:', error);
        alert('❌ Error al procesar la compra');
    }
}

// PERFIL - MIS BOLETOS
async function loadTickets() {
    if (!currentUser) {
        const listDiv = document.getElementById('ticketsList');
        listDiv.innerHTML = `
            <div class="empty-tickets">
                <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <rect x="2" y="7" width="20" height="4" rx="1"></rect>
                    <rect x="2" y="15" width="20" height="4" rx="1"></rect>
                    <path d="M12 3v18"></path>
                </svg>
                <p>Debes iniciar sesión para ver tus boletos</p>
                <button class="explore-btn" onclick="document.getElementById('loginModal').classList.add('active')">Iniciar Sesión</button>
            </div>
        `;
        return;
    }

    try {
        const response = await fetch('/api/boletos');
        const tickets = await response.json();

        const listDiv = document.getElementById('ticketsList');

        if (tickets.length === 0) {
            listDiv.innerHTML = `
                <div class="empty-tickets">
                    <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <rect x="2" y="7" width="20" height="4" rx="1"></rect>
                        <rect x="2" y="15" width="20" height="4" rx="1"></rect>
                        <path d="M12 3v18"></path>
                    </svg>
                    <p>No tienes boletos comprados</p>
                    <button class="explore-btn" onclick="switchView('home')">Explorar Cartelera</button>
                </div>
            `;
        } else {
            listDiv.innerHTML = tickets.map(ticket => `
                <div class="ticket-card">
                    <div class="ticket-header">
                        <div class="ticket-info">
                            <h3>${ticket.pelicula}</h3>
                            <p class="ticket-code">Código: ${ticket.codigo}</p>
                            <p class="ticket-date">${new Date(ticket.fecha).toLocaleString('es-CO')}</p>
                        </div>
                        <button class="cancel-btn" onclick="cancelTicket('${ticket.codigo}')">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                <line x1="18" y1="6" x2="6" y2="18"></line>
                                <line x1="6" y1="6" x2="18" y2="18"></line>
                            </svg>
                            CANCELAR
                        </button>
                    </div>
                    <div class="ticket-details">
                        <div class="ticket-detail-item">
                            <p>Horario</p>
                            <p>
                                <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                    <circle cx="12" cy="12" r="10"></circle>
                                    <polyline points="12 6 12 12 16 14"></polyline>
                                </svg>
                                ${ticket.horario}
                            </p>
                        </div>
                        <div class="ticket-detail-item">
                            <p>Asientos</p>
                            <p>${ticket.asientos.join(', ')}</p>
                        </div>
                        ${ticket.coleccionable ? `
                        <div class="ticket-detail-item">
                            <p>Coleccionable</p>
                            <p style="color: #f59e0b;">🎁 ${ticket.coleccionable}</p>
                        </div>
                        ` : ''}
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error al cargar boletos:', error);
    }
}

async function cancelTicket(codigo) {
    if (!confirm('¿Estás seguro de cancelar este boleto?')) return;

    try {
        const response = await fetch(`/api/cancelar/${codigo}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            alert('✅ Boleto cancelado exitosamente');
            // Los asientos se liberan automáticamente en el backend
            loadTickets();
        } else {
            alert('❌ Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error al cancelar:', error);
        alert('❌ Error al cancelar el boleto');
    }
}

// PANEL DE ADMINISTRACIÓN
function initAdminPanel() {
    const toggleBtn = document.getElementById('toggleAddForm');
    const form = document.getElementById('addMovieForm');

    toggleBtn.addEventListener('click', () => {
        form.style.display = form.style.display === 'none' ? 'block' : 'none';
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const movieData = {
            titulo: document.getElementById('movieTitle').value,
            genero: document.getElementById('movieGenre').value,
            duracion: document.getElementById('movieDuration').value,
            clasificacion: document.getElementById('movieRating').value,
            horarios: document.getElementById('movieSchedule').value.split(',').map(h => h.trim())
        };

        try {
            const response = await fetch('/api/admin/agregar-pelicula', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(movieData)
            });

            const data = await response.json();

            if (data.success) {
                alert('✅ Película agregada exitosamente');
                form.reset();
                form.style.display = 'none';
                await loadMovies();
                loadAdminData();
            } else {
                alert('❌ Error: ' + data.error);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('❌ Error al agregar película');
        }
    });
}

async function loadAdminData() {
    await loadAdminMovies();
    await loadStats();
}

async function loadAdminMovies() {
    const listDiv = document.getElementById('adminMoviesList');
    listDiv.innerHTML = movies.map((movie, idx) => `
        <div class="movie-item">
            <div class="movie-item-info">
                <h4>${movie.titulo}</h4>
                <p>${movie.genero}</p>
            </div>
            <button class="delete-btn" onclick="deleteMovie('${movie.titulo}')">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
            </button>
        </div>
    `).join('');
}

async function deleteMovie(titulo) {
    if (!confirm(`¿Eliminar "${titulo}"?`)) return;

    try {
        const response = await fetch(`/api/admin/eliminar-pelicula/${encodeURIComponent(titulo)}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            alert('✅ Película eliminada');
            await loadMovies();
            loadAdminData();
        } else {
            alert('❌ Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

async function loadStats() {
    try {
        const response = await fetch('/api/admin/estadisticas');
        const stats = await response.json();

        document.getElementById('statTopMovie').textContent = stats.topMovie;
        document.getElementById('statTopMovieSales').textContent = `${stats.topMovieSales} asientos vendidos`;

        document.getElementById('progressBar').style.width = `${stats.occupation}%`;
        document.getElementById('occupationPercent').textContent = `${stats.occupation}%`;
        document.getElementById('occupationDetails').textContent = `${stats.totalSold} / ${stats.totalCapacity} asientos vendidos`;

        // Gráfico de ventas
        const chartDiv = document.getElementById('salesChart');
        const maxSales = Math.max(...Object.values(stats.ventas_por_pelicula || {}));

        chartDiv.innerHTML = Object.entries(stats.ventas_por_pelicula || {}).map(([pelicula, ventas]) => {
            const percentage = maxSales > 0 ? (ventas / maxSales) * 100 : 0;
            return `
                <div class="chart-bar">
                    <div class="chart-bar-header">
                        <span>${pelicula}</span>
                        <span>${ventas}</span>
                    </div>
                    <div class="chart-bar-bg">
                        <div class="chart-bar-fill" style="width: ${percentage}%"></div>
                    </div>
                </div>
            `;
        }).join('');

    } catch (error) {
        console.error('Error al cargar estadísticas:', error);
    }
}