/**
 * Admin Dashboard JavaScript
 * Handles authentication, user statistics, and word cloud visualization
 */

const API_URL = 'https://time-tracker-1-3vqh.onrender.com/api/v1';

// State
let adminPassword = sessionStorage.getItem('adminPassword');

// DOM elements
const passwordScreen = document.getElementById('passwordScreen');
const adminDashboard = document.getElementById('adminDashboard');
const passwordForm = document.getElementById('passwordForm');
const adminPasswordInput = document.getElementById('adminPassword');
const passwordMessage = document.getElementById('passwordMessage');
const usersGrid = document.getElementById('usersGrid');
const loadingUsers = document.getElementById('loadingUsers');
const casualWordCloud = document.getElementById('casualWordCloud');
const seriousWordCloud = document.getElementById('seriousWordCloud');
const projectWordCloud = document.getElementById('projectWordCloud');
const wordCloudsContainer = document.getElementById('wordCloudsContainer');
const loadingCloud = document.getElementById('loadingCloud');
const logoutBtn = document.getElementById('logoutBtn');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    if (adminPassword) {
        showDashboard();
        loadData();
    } else {
        showPasswordScreen();
    }

    passwordForm.addEventListener('submit', handlePasswordSubmit);
    logoutBtn.addEventListener('click', handleLogout);
});

/**
 * Admin API call with password header
 */
async function adminApiCall(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        'X-Admin-Password': adminPassword,
        ...options.headers
    };

    const response = await fetch(`${API_URL}/admin${endpoint}`, {
        ...options,
        headers
    });

    if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
            // Invalid password - logout
            handleLogout();
            throw new Error('Invalid admin password');
        }
        throw new Error(`API call failed: ${response.statusText}`);
    }

    return response.json();
}

/**
 * Load all data
 */
async function loadData() {
    await Promise.all([
        loadUsersStats(),
        loadWordCloud()
    ]);
}

/**
 * Load users statistics
 */
async function loadUsersStats() {
    try {
        loadingUsers.style.display = 'block';
        usersGrid.style.display = 'none';

        const users = await adminApiCall('/users-stats');

        loadingUsers.style.display = 'none';
        usersGrid.style.display = 'grid';

        renderUsersGrid(users);
    } catch (error) {
        console.error('Failed to load users stats:', error);
        loadingUsers.textContent = 'שגיאה בטעינת נתונים';
        loadingUsers.className = 'message error-message';
    }
}

/**
 * Render users grid with pie charts
 */
function renderUsersGrid(users) {
    usersGrid.innerHTML = '';

    if (users.length === 0) {
        usersGrid.innerHTML = '<p style="text-align: center; color: #666;">אין משתמשים במערכת</p>';
        return;
    }

    users.forEach(user => {
        const userCard = createUserCard(user);
        usersGrid.appendChild(userCard);
    });
}

/**
 * Create user card with pie chart
 */
function createUserCard(user) {
    const card = document.createElement('div');
    card.className = 'user-card';

    const canvasId = `chart-${user.user_id}`;
    const createdDate = new Date(user.created_at).toLocaleDateString('he-IL');

    card.innerHTML = `
        <h3>${user.email}</h3>
        <div class="user-stats">
            <p><strong>תאריך הצטרפות:</strong> ${createdDate}</p>
            <p><strong>רישומים:</strong> ${user.entry_count}</p>
            <p><strong>פנאי מזדמן:</strong> ${user.casual_total.toFixed(1)} שעות</p>
            <p><strong>פנאי רציני:</strong> ${user.serious_total.toFixed(1)} שעות</p>
            <p><strong>פנאי פרויקט:</strong> ${user.project_total.toFixed(1)} שעות</p>
            <p><strong>סה"כ:</strong> ${user.total_hours.toFixed(1)} שעות</p>
        </div>
        <div class="pie-chart-container">
            <canvas id="${canvasId}"></canvas>
        </div>
    `;

    // Wait for DOM insertion
    setTimeout(() => {
        createPieChart(canvasId, user.leisure_distribution);
    }, 0);

    return card;
}

/**
 * Create pie chart for user
 */
function createPieChart(canvasId, distribution) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['פנאי מזדמן', 'פנאי רציני', 'פנאי פרויקט'],
            datasets: [{
                data: [
                    distribution.casual,
                    distribution.serious,
                    distribution.project
                ],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.7)',
                    'rgba(54, 162, 235, 0.7)',
                    'rgba(255, 206, 86, 0.7)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        font: { size: 10 },
                        color: '#333'
                    }
                }
            }
        }
    });
}

/**
 * Load word clouds
 */
async function loadWordCloud() {
    try {
        loadingCloud.style.display = 'block';
        wordCloudsContainer.style.display = 'none';

        const data = await adminApiCall('/word-cloud-data');

        loadingCloud.style.display = 'none';

        const totalNotes = data.casual_notes_count + data.serious_notes_count + data.project_notes_count;

        if (totalNotes === 0) {
            loadingCloud.style.display = 'block';
            loadingCloud.textContent = 'אין פעילויות לתצוגה';
            loadingCloud.className = 'message info-message';
            return;
        }

        wordCloudsContainer.style.display = 'grid';

        // Render three separate word clouds
        renderWordCloud(casualWordCloud, data.casual_text, 'rgba(255, 99, 132, 0.8)');
        renderWordCloud(seriousWordCloud, data.serious_text, 'rgba(54, 162, 235, 0.8)');
        renderWordCloud(projectWordCloud, data.project_text, 'rgba(255, 206, 86, 0.8)');
    } catch (error) {
        console.error('Failed to load word cloud:', error);
        loadingCloud.textContent = 'שגיאה בטעינת ענני מילים';
        loadingCloud.className = 'message error-message';
    }
}

/**
 * Render word cloud on a specific canvas
 */
function renderWordCloud(canvas, text, color) {
    if (!canvas) return;

    if (!text || text.trim().length === 0) {
        // Show "no data" message in canvas parent
        const wrapper = canvas.parentElement;
        wrapper.innerHTML = '<p style="text-align: center; color: #999; padding: 40px;">אין נתונים</p>';
        return;
    }

    // Process text into word frequencies
    const words = text.split(/\s+/);
    const wordFreq = {};

    words.forEach(word => {
        word = word.toLowerCase().trim();
        // Filter short words
        if (word.length > 2) {
            wordFreq[word] = (wordFreq[word] || 0) + 1;
        }
    });

    // Convert to array format for wordcloud2
    const wordList = Object.entries(wordFreq).map(([word, freq]) => [word, freq]);

    // Sort by frequency and take top 50 words per cloud
    wordList.sort((a, b) => b[1] - a[1]);
    const topWords = wordList.slice(0, 50);

    if (topWords.length === 0) {
        const wrapper = canvas.parentElement;
        wrapper.innerHTML = '<p style="text-align: center; color: #999; padding: 40px;">אין נתונים</p>';
        return;
    }

    // Render using wordcloud2.js
    try {
        WordCloud(canvas, {
            list: topWords,
            gridSize: 8,
            weightFactor: 2,
            fontFamily: 'Arial, sans-serif',
            color: color,
            rotateRatio: 0.3,
            backgroundColor: '#ffffff',
            drawOutOfBound: false,
            shrinkToFit: true
        });
    } catch (error) {
        console.error('Word cloud rendering error:', error);
        const wrapper = canvas.parentElement;
        wrapper.innerHTML = '<p style="text-align: center; color: #e74c3c; padding: 40px;">שגיאה בהצגת ענן מילים</p>';
    }
}

/**
 * Screen management
 */
function showPasswordScreen() {
    passwordScreen.style.display = 'block';
    adminDashboard.style.display = 'none';
}

function showDashboard() {
    passwordScreen.style.display = 'none';
    adminDashboard.style.display = 'block';
}

/**
 * Event handlers
 */
async function handlePasswordSubmit(e) {
    e.preventDefault();
    adminPassword = adminPasswordInput.value;
    sessionStorage.setItem('adminPassword', adminPassword);

    passwordMessage.textContent = 'מתחבר...';
    passwordMessage.className = 'message info-message';
    passwordMessage.style.display = 'block';

    // Test password by making API call
    try {
        await adminApiCall('/users-stats');
        showDashboard();
        loadData();
    } catch (error) {
        passwordMessage.textContent = 'סיסמה שגויה';
        passwordMessage.className = 'message error-message';
        adminPassword = null;
        sessionStorage.removeItem('adminPassword');
    }
}

function handleLogout() {
    adminPassword = null;
    sessionStorage.removeItem('adminPassword');
    showPasswordScreen();
    adminPasswordInput.value = '';
    passwordMessage.style.display = 'none';
}
