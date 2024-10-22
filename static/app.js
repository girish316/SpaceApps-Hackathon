document.addEventListener("DOMContentLoaded", function() {
    // Build the navbar when the page loads
    buildNavbar();

    // Depending on the page, call different functions to build the content
    if (window.location.pathname === '/') {
        buildHomePage();
    } else if (window.location.pathname === '/about') {
        buildIntroductionPage();
    } else if (window.location.pathname === '/profile') {
        buildProfilePage();
    } else if (window.location.pathname === '/blog') {
        buildBlogPage();  // Make sure blog page is built if on blog page
    }

    // Check if the user is logged in for both User button and Create Blog button
    checkIfUserLoggedIn();
});

// Function to dynamically build the navbar (shared across all pages)
function buildNavbar() {
    const app = document.getElementById('app');
    const navbar = document.createElement('nav');
    navbar.className = 'flex items-center justify-between bg-blue-900 p-4';

    // Build the navbar with buttons for Map, Introduction, Blog, and Users using TailwindCSS
    navbar.innerHTML = `
        <div class="logo">
            <a href="/"><img src="/static/hack.png" alt="Logo" class="h-10"></a>
        </div>
        <div class="flex space-x-4">
            <button class="bg-blue-900 text-white py-2 px-4 rounded hover:bg-cyan-500 hover:bg-opacity-20 transition duration-300" onclick="window.location.href='/map'">Map</button>
            <button class="bg-blue-900 text-white py-2 px-4 rounded hover:bg-cyan-500 hover:bg-opacity-20 transition duration-300" onclick="window.location.href='/about'">About</button>
            <button class="bg-blue-900 text-white py-2 px-4 rounded hover:bg-cyan-500 hover:bg-opacity-20 transition duration-300" onclick="window.location.href='/blog'">Blog</button>
            <button class="bg-blue-900 text-white py-2 px-4 rounded hover:bg-cyan-500 hover:bg-opacity-20 transition duration-300" onclick="window.location.href='/references'">References</button>
        </div>
        <div class="flex space-x-4">
            <button class="user-button bg-blue-900 text-white py-2 px-4 rounded hover:bg-cyan-500 hover:bg-opacity-20 transition duration-300">Profile</button>
        </div>
    `;
    app.appendChild(navbar);

    // Attach event listener for the Profile button
    document.querySelector('.user-button').addEventListener('click', function(e) {
        e.preventDefault();  // Prevent default link behavior
        checkIfUserLoggedIn().then(isLoggedIn => {
            if (isLoggedIn) {
                openUserSettingsModal();  // Open user settings modal if logged in
            } else {
                openLoginModal();  // Open login modal if not logged in
            }
        }).catch(error => {
            console.error('Error handling login status:', error);
        });
    });
}

// Function to check if the user is logged in and return a promise
function checkIfUserLoggedIn() {
    return fetch('/check_login')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (typeof data.logged_in === 'undefined') {
                throw new Error('Invalid response structure');
            }
            return data.logged_in;
        })
        .catch(error => {
            console.error('Error checking login status:', error);
            return false;  // Default to logged out in case of error
        });
}

// Open login modal (shared for both User and Create Blog buttons)
function openLoginModal() {
    closeModal(); // Ensure any existing modal is closed before opening a new one

    const modal = document.createElement('div');
    modal.className = 'modal fixed inset-0 bg-gray-800 bg-opacity-75 flex justify-center items-center';

    modal.innerHTML = `
        <div class="bg-white p-6 rounded shadow-lg relative">
            <button class="absolute top-2 right-2 text-gray-500" onclick="closeModal()">X</button>
            <h2 class="text-2xl font-bold mb-4">Login</h2>
            <input type="text" id="login-display-name" class="border p-2 w-full mb-2" placeholder="Display Name">
            <input type="password" id="login-password" class="border p-2 w-full mb-4" placeholder="Password">
            <button class="bg-blue-500 text-white p-2 rounded w-full" onclick="login()">Login</button>
            <p class="mt-4 text-center">Don't have an account? <span class="text-blue-500 cursor-pointer" onclick="openSignupModal()">Sign up</span></p>
        </div>
    `;
    document.body.appendChild(modal);
}

// Open user settings modal if logged in
function openUserSettingsModal() {
    closeModal(); // Close any existing modals

    const modal = document.createElement('div');
    modal.className = 'modal fixed inset-0 bg-gray-800 bg-opacity-75 flex justify-center items-center';

    modal.innerHTML = `
        <div class="bg-white p-6 rounded shadow-lg relative">
            <button class="absolute top-2 right-2 text-gray-500" onclick="closeModal()">X</button>
            <h2 class="text-2xl font-bold mb-4">User Settings</h2>
            <input type="text" id="edit-username" class="border p-2 w-full mb-2" placeholder="New Username">
            <input type="password" id="edit-password" class="border p-2 w-full mb-4" placeholder="New Password">
            <input type="password" id="old-password" class="border p-2 w-full mb-2" placeholder="Old Password (for confirmation)">
            <button class="bg-green-500 text-white p-2 rounded w-full mb-2" onclick="updateUserSettings()">Update</button>
            <button class="bg-red-500 text-white p-2 rounded w-full" onclick="logout()">Log Out</button>
        </div>
    `;
    document.body.appendChild(modal);
}

// Handle user settings update with old password confirmation
function updateUserSettings() {
    const oldPassword = document.getElementById('old-password').value;
    const newUsername = document.getElementById('edit-username').value;
    const newPassword = document.getElementById('edit-password').value;

    if (!oldPassword) {
        alert('Please enter your old password for confirmation.');
        return;
    }

    fetch('/update_profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ old_password: oldPassword, display_name: newUsername, password: newPassword })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            closeModal();
            alert('User settings updated successfully.');
        } else {
            alert('Error updating user settings: ' + (data.message || 'Unknown error'));
        }
    })
    .catch(error => {
        alert('Error: ' + error.message);
    });
}

// Handle user logout
function logout() {
    fetch('/logout', { method: 'POST' })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            closeModal();
            window.location.reload(); // Refresh the page after logout
        } else {
            alert('Error logging out.');
        }
    });
}

// Open sign-up modal (shared for both User and Create Blog buttons) with password validation
function openSignupModal() {
    closeModal(); // Ensure any existing modal is closed before opening a new one

    const modal = document.createElement('div');
    modal.className = 'modal fixed inset-0 bg-gray-800 bg-opacity-75 flex justify-center items-center';

    modal.innerHTML = `
        <div class="bg-white p-6 rounded shadow-lg relative">
            <button class="absolute top-2 right-2 text-gray-500" onclick="closeModal()">X</button>
            <h2 class="text-2xl font-bold mb-4">Sign Up</h2>
            <input type="text" id="signup-display-name" class="border p-2 w-full mb-2" placeholder="Display Name">
            <input type="password" id="signup-password" class="border p-2 w-full mb-4" placeholder="Password">
            <button class="bg-green-500 text-white p-2 rounded w-full" onclick="signup()">Sign Up</button>
            <p class="mt-4 text-center">Already have an account? <span class="text-blue-500 cursor-pointer" onclick="openLoginModal()">Log in</span></p>
        </div>
    `;
    document.body.appendChild(modal);
}

// Handle user signup process with password validation
function signup() {
    const displayName = document.getElementById('signup-display-name').value;
    const password = document.getElementById('signup-password').value;

    // Password validation
    const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{7,}$/;  // At least one letter, one number, and 7 characters minimum
    if (!passwordRegex.test(password)) {
        alert('Password must be at least 7 characters long and contain at least one letter and one number.');
        return;
    }

    // Proceed with signup if the password is valid
    fetch('/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ display_name: displayName, password: password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            closeModal();
            openLoginModal(); // Open the login modal after successful signup
        } else {
            alert(data.message || 'Error signing up.');
        }
    })
    .catch(err => console.error('Error during signup:', err));
}

// Function to handle user login process
function login() {
    const displayName = document.getElementById('login-display-name').value;
    const password = document.getElementById('login-password').value;

    fetch('/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ display_name: displayName, password: password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            closeModal();
            alert('Login successful.');
            window.location.reload(); // Reload the page to reflect login status
        } else {
            alert('Invalid login credentials.');
        }
    });
}

// Function to close the modal
function closeModal() {
    const modal = document.querySelector('.modal');
    if (modal) {
        modal.remove();
    }
}
