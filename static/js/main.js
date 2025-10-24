// Main JavaScript for Rogue Detection System

// Initialize Socket.IO connection
let socket;

document.addEventListener('DOMContentLoaded', function() {
    // Only initialize socket if user is logged in (navbar exists)
    if (document.querySelector('.navbar')) {
        initializeSocket();
    }
    
    // Update last scan time
    updateLastScanTime();
});

function initializeSocket() {
    socket = io();
    
    socket.on('connect', function() {
        console.log('Connected to server');
    });
    
    socket.on('scan_complete', function(data) {
        console.log('Scan completed:', data);
        showNotification('Scan Complete', `Found ${data.total_devices} devices (${data.rogues} rogues)`, 'info');
        updateLastScanTime();
        
        // Reload current page data
        if (typeof loadRogueDevices === 'function') {
            loadRogueDevices();
        }
        if (typeof updateStats === 'function') {
            updateStats();
        }
    });
    
    socket.on('device_authorized', function(data) {
        console.log('Device authorized:', data);
        showNotification('Device Authorized', `Device ${data.mac_address} has been authorized`, 'success');
    });
    
    socket.on('device_isolated', function(data) {
        console.log('Device isolated:', data);
        showNotification('Device Isolated', `Device on port ${data.port} has been isolated`, 'warning');
    });
    
    socket.on('device_restored', function(data) {
        console.log('Device restored:', data);
        showNotification('Device Restored', `Device on port ${data.port} has been restored`, 'info');
    });
}

function triggerScan() {
    showNotification('Scan Started', 'Network scan in progress...', 'info');
    
    fetch('/api/scan', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Scan results:', data);
            } else {
                showNotification('Scan Failed', data.error || 'Unknown error', 'danger');
            }
        })
        .catch(error => {
            console.error('Scan error:', error);
            showNotification('Scan Error', 'Failed to initiate scan', 'danger');
        });
}

function showNotification(title, message, type = 'info') {
    // Create toast notification
    const toastContainer = getToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <strong>${title}</strong><br>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast, { delay: 5000 });
    bsToast.show();
    
    // Remove toast after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

function getToastContainer() {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
    return container;
}

function updateLastScanTime() {
    const element = document.getElementById('lastScanTime');
    if (!element) return;
    
    fetch('/api/monitoring/status')
        .then(response => response.json())
        .then(data => {
            if (data.latest_scan && data.latest_scan.timestamp) {
                const scanTime = new Date(data.latest_scan.timestamp);
                element.textContent = scanTime.toLocaleTimeString();
            } else {
                element.textContent = 'Never';
            }
        })
        .catch(error => {
            console.error('Error fetching scan time:', error);
        });
}

// Update last scan time every 10 seconds
setInterval(updateLastScanTime, 10000);

// Utility functions
function formatMacAddress(mac) {
    return mac.toUpperCase().match(/.{1,2}/g).join(':');
}

function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString();
}

function getSeverityBadgeClass(severity) {
    const classes = {
        'CRITICAL': 'danger',
        'HIGH': 'warning',
        'MEDIUM': 'info',
        'LOW': 'secondary',
        'INFO': 'primary'
    };
    return classes[severity] || 'secondary';
}

function getStatusBadgeClass(status) {
    const classes = {
        'active': 'success',
        'isolated': 'danger',
        'unknown': 'secondary'
    };
    return classes[status] || 'secondary';
}

