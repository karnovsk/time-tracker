// Configuration
const API_URL = 'http://localhost:8000/api/v1';

// State
let accessToken = localStorage.getItem('accessToken');
let currentUser = null;
let currentChart = null;
let currentPage = 1;
const pageSize = 10;

// DOM Elements
const loginScreen = document.getElementById('loginScreen');
const dashboardScreen = document.getElementById('dashboardScreen');
const loginForm = document.getElementById('loginForm');
const verifyForm = document.getElementById('verifyForm');
const sendOtpBtn = document.getElementById('sendOtpBtn');
const verifyBtn = document.getElementById('verifyBtn');
const backBtn = document.getElementById('backBtn');
const logoutBtn = document.getElementById('logoutBtn');
const loginMessage = document.getElementById('loginMessage');
const userEmail = document.getElementById('userEmail');
const todayDate = document.getElementById('todayDate');
const entryForm = document.getElementById('entryForm');
const entryFormCard = document.getElementById('entryFormCard');
const alreadySubmittedMessage = document.getElementById('alreadySubmittedMessage');
const todayEntryDisplay = document.getElementById('todayEntryDisplay');
const entryMessage = document.getElementById('entryMessage');
const toggleStatsBtn = document.getElementById('toggleStatsBtn');
const statisticsSection = document.getElementById('statisticsSection');
const chartType = document.getElementById('chartType');
const resetDataBtn = document.getElementById('resetDataBtn');
const prevPageBtn = document.getElementById('prevPageBtn');
const nextPageBtn = document.getElementById('nextPageBtn');
const pageInfo = document.getElementById('pageInfo');
const shareStatsBtn = document.getElementById('shareStatsBtn');

// Initialize
document.addEventListener('DOMContentLoaded', init);

async function init() {
    // Set today's date
    todayDate.textContent = new Date().toLocaleDateString('he-IL');

    // Auto-login if token exists
    if (accessToken) {
        try {
            await loadCurrentUser();
            showDashboard();
        } catch (error) {
            // Token invalid, clear and show login
            localStorage.removeItem('accessToken');
            accessToken = null;
            showLogin();
        }
    } else {
        showLogin();
    }

    // Event listeners
    loginForm.addEventListener('submit', handleSendOTP);
    verifyForm.addEventListener('submit', handleVerifyOTP);
    backBtn.addEventListener('click', () => {
        loginForm.style.display = 'block';
        verifyForm.style.display = 'none';
    });
    logoutBtn.addEventListener('click', handleLogout);
    entryForm.addEventListener('submit', handleSubmitEntry);
    toggleStatsBtn.addEventListener('click', toggleStatistics);
    chartType.addEventListener('change', updateChart);
    resetDataBtn.addEventListener('click', handleResetData);
    prevPageBtn.addEventListener('click', () => changePage(currentPage - 1));
    nextPageBtn.addEventListener('click', () => changePage(currentPage + 1));
    shareStatsBtn.addEventListener('click', handleShareStatistics);

    // Hour inputs - update total
    ['casualHours', 'seriousHours', 'projectHours'].forEach(id => {
        document.getElementById(id).addEventListener('input', updateTotalHours);
    });
}

// API Functions
async function apiCall(endpoint, options = {}) {
    const url = `${API_URL}${endpoint}`;
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    if (accessToken) {
        headers['Authorization'] = `Bearer ${accessToken}`;
    }

    const response = await fetch(url, {
        ...options,
        headers
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Request failed');
    }

    if (response.status === 204) {
        return null;
    }

    return response.json();
}

// Authentication Functions
async function handleSendOTP(e) {
    e.preventDefault();
    const email = document.getElementById('email').value;

    try {
        sendOtpBtn.disabled = true;
        sendOtpBtn.textContent = 'שולח...';

        await apiCall('/auth/send-otp', {
            method: 'POST',
            body: JSON.stringify({ email })
        });

        showMessage(loginMessage, 'קוד אימות נשלח לאימייל שלך', 'success');
        loginForm.style.display = 'none';
        verifyForm.style.display = 'block';
    } catch (error) {
        showMessage(loginMessage, error.message, 'error');
    } finally {
        sendOtpBtn.disabled = false;
        sendOtpBtn.textContent = 'שלח קוד אימות';
    }
}

async function handleVerifyOTP(e) {
    e.preventDefault();
    const email = document.getElementById('email').value;
    const otp = document.getElementById('otp').value;

    try {
        verifyBtn.disabled = true;
        verifyBtn.textContent = 'מאמת...';

        const data = await apiCall('/auth/verify-otp', {
            method: 'POST',
            body: JSON.stringify({ email, otp })
        });

        accessToken = data.access_token;
        localStorage.setItem('accessToken', accessToken);
        currentUser = data.user;

        showDashboard();
    } catch (error) {
        showMessage(loginMessage, 'קוד אימות שגוי', 'error');
    } finally {
        verifyBtn.disabled = false;
        verifyBtn.textContent = 'אמת והתחבר';
    }
}

async function loadCurrentUser() {
    const data = await apiCall('/auth/me');
    currentUser = data;
}

function handleLogout() {
    localStorage.removeItem('accessToken');
    accessToken = null;
    currentUser = null;
    showLogin();
}

// Screen Functions
function showLogin() {
    loginScreen.style.display = 'flex';
    dashboardScreen.style.display = 'none';
    loginForm.reset();
    verifyForm.reset();
    loginForm.style.display = 'block';
    verifyForm.style.display = 'none';
    loginMessage.textContent = '';
}

async function showDashboard() {
    loginScreen.style.display = 'none';
    dashboardScreen.style.display = 'block';
    userEmail.textContent = currentUser.email;

    await checkCanSubmit();
}

// Entry Functions
async function checkCanSubmit() {
    try {
        const data = await apiCall('/entries/can-submit');

        // Always show form to allow retroactive entry submission
        entryForm.style.display = 'block';

        if (!data.can_submit) {
            // Show info message about today's entry, but keep form visible for other dates
            alreadySubmittedMessage.style.display = 'block';
            displayTodayEntry(data.existing_entry);
        } else {
            alreadySubmittedMessage.style.display = 'none';
        }
    } catch (error) {
        console.error('Failed to check submission status:', error);
    }
}

function displayTodayEntry(entry) {
    todayEntryDisplay.innerHTML = `
        <div style="margin-top: 15px;">
            <p><strong>פנאי מזדמן:</strong> ${entry.casual_leisure_hours} שעות - ${entry.casual_leisure_note || 'ללא תיאור'}</p>
            <p><strong>פנאי רציני:</strong> ${entry.serious_leisure_hours} שעות - ${entry.serious_leisure_note || 'ללא תיאור'}</p>
            <p><strong>פנאי פרויקט:</strong> ${entry.project_leisure_hours} שעות - ${entry.project_leisure_note || 'ללא תיאור'}</p>
            <p><strong>סה"כ:</strong> ${entry.total_hours} שעות</p>
        </div>
    `;
}

function updateTotalHours() {
    const casual = parseFloat(document.getElementById('casualHours').value) || 0;
    const serious = parseFloat(document.getElementById('seriousHours').value) || 0;
    const project = parseFloat(document.getElementById('projectHours').value) || 0;
    const total = casual + serious + project;
    document.getElementById('totalHours').textContent = total.toFixed(1);
}

async function handleSubmitEntry(e) {
    e.preventDefault();

    const data = {
        casual_leisure_hours: parseFloat(document.getElementById('casualHours').value),
        casual_leisure_note: document.getElementById('casualNote').value.trim() || null,
        serious_leisure_hours: parseFloat(document.getElementById('seriousHours').value),
        serious_leisure_note: document.getElementById('seriousNote').value.trim() || null,
        project_leisure_hours: parseFloat(document.getElementById('projectHours').value),
        project_leisure_note: document.getElementById('projectNote').value.trim() || null
    };

    // Add optional entry_date for retroactive entries
    const entryDateInput = document.getElementById('entryDate');
    if (entryDateInput && entryDateInput.value) {
        data.entry_date = entryDateInput.value;
    }

    if (data.casual_leisure_hours + data.serious_leisure_hours + data.project_leisure_hours === 0) {
        showMessage(entryMessage, 'סה"כ שעות חייב להיות גדול מ-0', 'error');
        return;
    }

    try {
        const submitBtn = document.getElementById('submitEntryBtn');
        submitBtn.disabled = true;
        submitBtn.textContent = 'שולח...';

        await apiCall('/entries/today', {
            method: 'POST',
            body: JSON.stringify(data)
        });

        showMessage(entryMessage, 'הרישום נשלח בהצלחה!', 'success');
        entryForm.reset();
        updateTotalHours();

        // Refresh the form state
        await checkCanSubmit();
    } catch (error) {
        showMessage(entryMessage, error.message, 'error');
    } finally {
        const submitBtn = document.getElementById('submitEntryBtn');
        submitBtn.disabled = false;
        submitBtn.textContent = 'שלח רישום';
    }
}

// Statistics Functions
async function toggleStatistics() {
    if (statisticsSection.style.display === 'none') {
        statisticsSection.style.display = 'block';
        toggleStatsBtn.textContent = 'הסתר סטטיסטיקה';
        document.getElementById('statsUserEmail').textContent = currentUser.email;
        await loadStatistics();
        await loadHistory();
    } else {
        statisticsSection.style.display = 'none';
        toggleStatsBtn.textContent = 'הצג סטטיסטיקה';
    }
}

async function loadStatistics() {
    try {
        const data = await apiCall('/statistics/overview');

        // Update stats display
        document.getElementById('casualTotal').textContent = data.casual_leisure.total_hours;
        document.getElementById('casualAvg').textContent = data.casual_leisure.average_hours;
        document.getElementById('seriousTotal').textContent = data.serious_leisure.total_hours;
        document.getElementById('seriousAvg').textContent = data.serious_leisure.average_hours;
        document.getElementById('projectTotal').textContent = data.project_leisure.total_hours;
        document.getElementById('projectAvg').textContent = data.project_leisure.average_hours;
        document.getElementById('overallTotal').textContent = data.total_hours;
        document.getElementById('overallAvg').textContent = data.average_total_hours;
        document.getElementById('totalEntries').textContent = data.total_entries;

        // Update chart
        updateChart();
    } catch (error) {
        console.error('Failed to load statistics:', error);
    }
}

async function updateChart() {
    const data = await apiCall('/statistics/overview');
    const type = chartType.value;

    const ctx = document.getElementById('statsChart');

    if (currentChart) {
        currentChart.destroy();
    }

    const chartData = {
        labels: ['פנאי מזדמן', 'פנאי רציני', 'פנאי פרויקט'],
        datasets: [{
            label: 'שעות',
            data: [
                data.casual_leisure.total_hours,
                data.serious_leisure.total_hours,
                data.project_leisure.total_hours
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
            borderWidth: 2
        }]
    };

    currentChart = new Chart(ctx, {
        type: type,
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom'
                }
            }
        }
    });
}

async function loadHistory() {
    try {
        const data = await apiCall(`/entries/history?page=${currentPage}&page_size=${pageSize}`);

        const tbody = document.getElementById('historyTableBody');
        tbody.innerHTML = '';

        if (data.entries.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align: center;">אין רישומים</td></tr>';
        } else {
            data.entries.forEach(entry => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${new Date(entry.entry_date).toLocaleDateString('he-IL')}</td>
                    <td>${entry.casual_leisure_hours}h</td>
                    <td>${entry.casual_leisure_note || '-'}</td>
                    <td>${entry.serious_leisure_hours}h</td>
                    <td>${entry.serious_leisure_note || '-'}</td>
                    <td>${entry.project_leisure_hours}h</td>
                    <td>${entry.project_leisure_note || '-'}</td>
                    <td><strong>${entry.total_hours}h</strong></td>
                `;
                tbody.appendChild(row);
            });
        }

        // Update pagination
        pageInfo.textContent = `עמוד ${data.page} מתוך ${data.total_pages}`;
        prevPageBtn.disabled = data.page <= 1;
        nextPageBtn.disabled = data.page >= data.total_pages;
    } catch (error) {
        console.error('Failed to load history:', error);
    }
}

function changePage(page) {
    currentPage = page;
    loadHistory();
}

async function handleResetData() {
    if (!confirm('האם אתה בטוח שברצונך למחוק את כל הנתונים? פעולה זו לא ניתנת לשחזור!')) {
        return;
    }

    if (!confirm('אישור אחרון: זה ימחק לצמיתות את כל הרישומים שלך!')) {
        return;
    }

    try {
        resetDataBtn.disabled = true;
        resetDataBtn.textContent = 'מוחק...';

        await apiCall('/statistics/reset', {
            method: 'DELETE'
        });

        alert('כל הנתונים נמחקו בהצלחה');

        // Refresh dashboard
        statisticsSection.style.display = 'none';
        toggleStatsBtn.textContent = 'הצג סטטיסטיקה';
        await checkCanSubmit();
    } catch (error) {
        alert('שגיאה במחיקת נתונים: ' + error.message);
    } finally {
        resetDataBtn.disabled = false;
        resetDataBtn.textContent = 'אפס את כל הנתונים';
    }
}

async function handleShareStatistics() {
    try {
        shareStatsBtn.disabled = true;
        shareStatsBtn.textContent = 'מכין תמונה...';

        // Capture the statistics section as canvas
        const statsSection = document.getElementById('statisticsSection');
        const canvas = await html2canvas(statsSection, {
            backgroundColor: '#ffffff',
            scale: 2, // Higher quality
            logging: false,
            useCORS: true
        });

        // Convert canvas to blob
        canvas.toBlob(async (blob) => {
            const file = new File([blob], 'statistics.png', { type: 'image/png' });

            // Try to use Web Share API (works on mobile and some browsers)
            if (navigator.share && navigator.canShare && navigator.canShare({ files: [file] })) {
                try {
                    await navigator.share({
                        title: 'סטטיסטיקת זמן פנאי',
                        text: 'הסטטיסטיקה שלי ממעקב זמן פנאי',
                        files: [file]
                    });
                    alert('שותף בהצלחה!');
                } catch (shareError) {
                    if (shareError.name !== 'AbortError') {
                        // If share was cancelled, don't show error
                        downloadImage(canvas);
                    }
                }
            } else {
                // Fallback: Download the image
                downloadImage(canvas);
            }
        }, 'image/png');

    } catch (error) {
        console.error('Failed to share statistics:', error);
        alert('שגיאה ביצירת תמונה. נסה שוב.');
    } finally {
        shareStatsBtn.disabled = false;
        shareStatsBtn.textContent = '📊 שתף סטטיסטיקה';
    }
}

function downloadImage(canvas) {
    // Create download link
    const link = document.createElement('a');
    link.download = `statistics-${new Date().toLocaleDateString('he-IL')}.png`;
    link.href = canvas.toDataURL('image/png');
    link.click();
    alert('התמונה הורדה בהצלחה!');
}

// Utility Functions
function showMessage(element, message, type) {
    element.textContent = message;
    element.className = `message ${type}`;
    element.style.display = 'block';

    setTimeout(() => {
        element.style.display = 'none';
    }, 5000);
}
