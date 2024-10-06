document.addEventListener("DOMContentLoaded", function () {
    // Build the navbar when the page loads
    buildNavbar();

    // Build the blog page content
    buildBlogPage();

    // Check if the user is logged in and set up the Create Blog button accordingly
    checkIfUserLoggedIn().then(isLoggedIn => {
        if (isLoggedIn) {
            setupLoggedInUI();
        } else {
            setupLoggedOutUI();
        }
    });
});

// Function to dynamically build the navbar on the blog page
function buildNavbar() {
    const app = document.getElementById('app');
    const navbar = document.createElement('nav');
    navbar.className = 'flex items-center justify-between bg-blue-900 p-4';

    // Updated navbar with buttons for Map, Introduction, Blog, and Users using TailwindCSS
    navbar.innerHTML = `
        <div class="logo">
            <a href="/"><img src="/static/hack.png" alt="Logo" class="h-10"></a>
        </div>
        <div class="flex space-x-4">
            <button class="bg-blue-900 text-white py-2 px-4 rounded hover:bg-cyan-500 hover:bg-opacity-20 transition duration-300" onclick="window.location.href='/map'">Map</button>
            <button class="bg-blue-900 text-white py-2 px-4 rounded hover:bg-cyan-500 hover:bg-opacity-20 transition duration-300" onclick="window.location.href='/introduction'">Introduction</button>
            <button class="bg-blue-900 text-white py-2 px-4 rounded hover:bg-cyan-500 hover:bg-opacity-20 transition duration-300" onclick="window.location.href='/blog'">Blog</button>
        </div>
        <div class="flex space-x-4">
            <button class="user-button bg-blue-900 text-white py-2 px-4 rounded hover:bg-cyan-500 hover:bg-opacity-20 transition duration-300">Profile</button>
        </div>
    `;
    app.appendChild(navbar);

    // Attach event listener for the Users button
    document.querySelector('.user-button').addEventListener('click', function(e) {
        e.preventDefault();
        // Check if user is logged in before deciding which modal to open
        checkIfUserLoggedIn().then(isLoggedIn => {
            if (isLoggedIn) {
                openUserSettingsModal();
            } else {
                openLoginModal();
            }
        });
    });
}

// Function to check if the user is logged in and return a promise
function checkIfUserLoggedIn() {
    return fetch('/check_login')
        .then(response => response.json())
        .then(data => data.logged_in);
}

// Setup the UI for a logged-in user (Create Blog button enabled)
function setupLoggedInUI() {
    const createBlogBtn = document.getElementById('create-blog-btn');
    if (createBlogBtn) {
        createBlogBtn.disabled = false;
        createBlogBtn.addEventListener('click', createBlog);
    }
}

// Setup the UI for a logged-out user (Create Blog button still clickable, shows login modal)
function setupLoggedOutUI() {
    const createBlogBtn = document.getElementById('create-blog-btn');
    if (createBlogBtn) {
        createBlogBtn.disabled = false; // Ensure the button is always clickable
        createBlogBtn.addEventListener('click', function () {
            openLoginModal();  // Open login modal if not logged in
        });
    }
}

// Open login modal
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

// Open sign-up modal
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

// Handle user login
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

// Handle user signup
function signup() {
    const displayName = document.getElementById('signup-display-name').value;
    const password = document.getElementById('signup-password').value;

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
    });
}

// Function to close the modal
function closeModal() {
    const modal = document.querySelector('.modal');
    if (modal) {
        modal.remove();
    }
}

// Open user settings modal (added old password field for confirmation, now moved to last)
function openUserSettingsModal() {
    closeModal();

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

    // Check if old password is provided
    if (!oldPassword) {
        alert('Please enter your old password for confirmation.');
        return;
    }

    fetch('/update_profile', {  // Updated the route to match the one in app.py
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            old_password: oldPassword, 
            display_name: newUsername,  // Use "display_name" as in your app.py
            password: newPassword
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('404 - Endpoint not found');
        }
        return response.json();
    })
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

// Function to dynamically build the blog page content
function buildBlogPage() {
    const app = document.getElementById('app');
    const mainContent = document.createElement('div');
    mainContent.className = 'p-6';

    mainContent.innerHTML = `
        <h1 class="text-4xl font-bold mb-4">Community Blogs</h1>
        <div class="blog-container">
            <!-- Blogs will be loaded dynamically here -->
        </div>
        <div class="create-blog mt-6">
            <textarea id="blog-content" class="border p-2 w-full" placeholder="Write a new blog"></textarea><br>
            <button class="bg-green-500 text-white p-2 mt-2 rounded" id="create-blog-btn">Create Blog</button>
        </div>
    `;

    app.appendChild(mainContent);

    loadBlogs();  // Call the function to load blogs
}

// Function to load blogs dynamically via AJAX and insert them into the DOM
function loadBlogs() {
    fetch('/get_blogs')
        .then(response => response.json())
        .then(data => {
            const blogContainer = document.querySelector('.blog-container');
            blogContainer.innerHTML = ''; // Clear existing content
            data.blogs.forEach(blog => {
                const blogPost = document.createElement('div');
                blogPost.className = 'border p-4 mb-4 bg-white rounded-lg shadow-md';
                blogPost.innerHTML = `
                    <p class="text-lg">${blog.content}</p>
                    <button class="bg-blue-500 text-white p-2 rounded" onclick="editBlog(${blog.id})">Edit</button>
                    <button class="bg-red-500 text-white p-2 ml-2 rounded" onclick="deleteBlog(${blog.id})">Delete</button>
                `;
                blogContainer.appendChild(blogPost);
            });
        });
}

// Function to create a new blog post
function createBlog() {
    const content = document.getElementById('blog-content').value;

    fetch('/create_blog', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: content })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadBlogs();  // Reload blogs after creating a new one
            document.getElementById('blog-content').value = '';  // Clear input
        } else {
            alert('Error creating blog.');
        }
    });
}

// Function to edit an existing blog post
function editBlog(blogId) {
    const newContent = prompt('Edit your blog content:');
    if (newContent) {
        fetch(`/edit_blog/${blogId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content: newContent })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadBlogs();  // Reload blogs after editing
            } else {
                alert('Error editing blog.');
            }
        });
    }
}

// Function to delete a blog post
function deleteBlog(blogId) {
    fetch(`/delete_blog/${blogId}`, { method: 'POST' })
        .then(() => loadBlogs());  // Reload blogs after deletion
}
