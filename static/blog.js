document.addEventListener("DOMContentLoaded", function () {
    buildNavbar();

    buildBlogPage();

    checkIfUserLoggedIn().then(isLoggedIn => {
        if (isLoggedIn) {
            setupLoggedInUI();
        } else {
            setupLoggedOutUI();
        }
    });
});

function buildNavbar() {
    const app = document.getElementById('app');
    if (!app) return;
    const navbar = document.createElement('nav');
    navbar.className = 'flex items-center justify-between bg-blue-900 p-4';

    navbar.innerHTML = `
        <div class="logo">
            <a href="/"><img src="/static/hack.png" alt="Logo" class="h-10"></a>
        </div>
        <div class="flex space-x-4">
            <button class="bg-blue-900 text-white py-2 px-4 rounded hover:bg-cyan-500 hover:bg-opacity-20 transition duration-300" onclick="window.location.href='/map'">Map</button>
            <button class="bg-blue-900 text-white py-2 px-4 rounded hover:bg-cyan-500 hover:bg-opacity-20 transition duration-300" onclick="window.location.href='/introduction'">About</button>
            <button class="bg-blue-900 text-white py-2 px-4 rounded hover:bg-cyan-500 hover:bg-opacity-20 transition duration-300" onclick="window.location.href='/blog'">Blog</button>
            <button class="bg-blue-900 text-white py-2 px-4 rounded hover:bg-cyan-500 hover:bg-opacity-20 transition duration-300" onclick="window.location.href='/references'">References</button>
        </div>
        <div class="flex space-x-4">
            <button class="user-button bg-blue-900 text-white py-2 px-4 rounded hover:bg-cyan-500 hover:bg-opacity-20 transition duration-300">Profile</button>
        </div>
    `;
    app.appendChild(navbar);

    document.querySelector('.user-button').addEventListener('click', function(e) {
        e.preventDefault();
        checkIfUserLoggedIn().then(isLoggedIn => {
            if (isLoggedIn) {
                openUserSettingsModal();
            } else {
                openLoginModal();
            }
        }).catch(error => {
            console.error('Error handling login status:', error);
        });
    });
}

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
            return false;
        });
}

function setupLoggedInUI() {
    const createBlogBtn = document.getElementById('create-blog-btn');
    if (createBlogBtn) {
        createBlogBtn.disabled = false;
        createBlogBtn.addEventListener('click', createBlog);
    }
}

function setupLoggedOutUI() {
    const createBlogBtn = document.getElementById('create-blog-btn');
    if (createBlogBtn) {
        createBlogBtn.disabled = false;
        createBlogBtn.addEventListener('click', function () {
            openLoginModal();
        });
    }
}

function openLoginModal() {
    closeModal();

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

function closeModal() {
    const modal = document.querySelector('.modal');
    if (modal) {
        modal.remove();
    }
}

function createBlog() {
    const title = document.getElementById('blog-title').value;
    const content = document.getElementById('blog-content').value;

    fetch('/create_blog', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: title, content: content })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadBlogs();
            document.getElementById('blog-title').value = '';
            document.getElementById('blog-content').value = '';
        } else {
            alert('Error creating blog.');
        }
    })
    .catch(err => console.error('Error creating blog:', err));
}

function loadBlogs() {
    fetch('/get_blogs')
        .then(response => response.json())
        .then(data => {
            const blogContainer = document.querySelector('.blog-container');
            
            blogContainer.innerHTML = '';
            data.blogs.forEach(blog => {
                const blogPost = document.createElement('div');
                blogPost.className = 'border p-10 mb-4 bg-white rounded-lg shadow-md';
                blogPost.innerHTML = `
                    <p><strong>${blog.username}</strong></p>
                    <input class="font-bold text-xl mb-2 border p-2 w-full blog-title-${blog.id}" value="${blog.title}" readonly>
                    <textarea class="text-lg border p-2 w-full blog-content-${blog.id} expandable-textarea" readonly data-expanded="false" style="height: 100px;">${blog.content}</textarea>
                    <button class="bg-gray-500 text-white p-2 rounded mt-2 read-more-btn" data-blog-id="${blog.id}">Read More</button>
                    <button class="bg-gray-500 text-white p-2 rounded mt-2 shrink-btn" data-blog-id="${blog.id}" style="display: none;">Shrink</button>
                    <div class="mt-4">
                        ${data.current_user_id === blog.user_id ? `
                            <button class="bg-blue-500 text-white p-2 rounded mr-2" style="margin-top: 10px;" onclick="editBlog(${blog.id})">Edit</button>
                            <button class="bg-red-500 text-white p-2 rounded" style="margin-top: 10px;" onclick="deleteBlog(${blog.id})">Delete</button>
                        ` : ''}
                    </div>
                `;
                blogContainer.appendChild(blogPost);

                const readMoreBtn = blogPost.querySelector(`.read-more-btn[data-blog-id="${blog.id}"]`);
                const shrinkBtn = blogPost.querySelector(`.shrink-btn[data-blog-id="${blog.id}"]`);
                const textarea = blogPost.querySelector(`.blog-content-${blog.id}`);

                readMoreBtn.addEventListener('click', function() {
                    textarea.style.height = 'auto'; 
                    textarea.style.height = textarea.scrollHeight + 'px';
                    textarea.dataset.expanded = 'true';
                    readMoreBtn.style.display = 'none';
                    shrinkBtn.style.display = 'inline-block';
                });

                shrinkBtn.addEventListener('click', function() {
                    textarea.style.height = '100px';
                    textarea.dataset.expanded = 'false';
                    readMoreBtn.style.display = 'inline-block';
                    shrinkBtn.style.display = 'none';
                });
            });
        })
        .catch(err => console.error('Error loading blogs:', err));
}




function buildBlogPage() {
    const app = document.getElementById('app');
    if (!app) return;

    const mainContent = document.createElement('div');
    mainContent.className = 'p-6';

    mainContent.innerHTML = `
        <h1 class="text-4xl font-bold mb-4">Community Blogs</h1>
        <div class="create-blog mb-6">
            <input id="blog-title" class="border p-2 w-full mb-2" placeholder="Blog Title"><br>
            <textarea id="blog-content" class="border p-2 w-full" placeholder="Write a new blog"></textarea><br>
            <button class="bg-green-500 text-white p-2 mt-2 rounded" id="create-blog-btn">Create Blog</button>
        </div>
        <div class="blog-container">
            <!-- Blogs will be loaded dynamically here -->
        </div>
    `;

    app.appendChild(mainContent);

    setupCreateBlog();

    loadBlogs();
}

function setupCreateBlog() {
    const createBlogBtn = document.getElementById('create-blog-btn');
    createBlogBtn.addEventListener('click', createBlog);
}

function editBlog(blogId) {
    const titleInput = document.querySelector(`.blog-title-${blogId}`);
    const contentTextarea = document.querySelector(`.blog-content-${blogId}`);
    const editButton = document.querySelector(`button[onclick="editBlog(${blogId})"]`);

    if (titleInput.readOnly) {
        titleInput.readOnly = false;
        contentTextarea.readOnly = false;
        titleInput.classList.add('border-blue-500');
        contentTextarea.classList.add('border-blue-500');
        editButton.textContent = 'Save';
    } else {
        const newTitle = titleInput.value;
        const newContent = contentTextarea.value;

        fetch(`/edit_blog/${blogId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: newTitle, content: newContent })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                titleInput.readOnly = true;
                contentTextarea.readOnly = true;
                titleInput.classList.remove('border-blue-500');
                contentTextarea.classList.remove('border-blue-500');
                editButton.textContent = 'Edit';
                loadBlogs();
            } else {
                alert('Error saving blog.');
            }
        })
        .catch(err => console.error('Error saving blog:', err));
    }
}

function deleteBlog(blogId) {
    fetch(`/delete_blog/${blogId}`, { method: 'POST' })
        .then(() => loadBlogs())
        .catch(err => console.error('Error deleting blog:', err));
}

function openSignupModal() {
    closeModal();

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

function signup() {
    const displayName = document.getElementById('signup-display-name').value;
    const password = document.getElementById('signup-password').value;

    const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{7,}$/;
    if (!passwordRegex.test(password)) {
        alert('Password must be at least 7 characters long and contain at least one letter and one number.');
        return;
    }

    fetch('/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ display_name: displayName, password: password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            closeModal();
            openLoginModal();
        } else {
            alert(data.message || 'Error signing up.');
        }
    })
    .catch(err => console.error('Error during signup:', err));
}

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
            window.location.reload();
        } else {
            alert('Invalid login credentials.');
        }
    });
}

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

function logout() {
    fetch('/logout', { method: 'POST' })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            closeModal();
            window.location.reload(); 
        } else {
            alert('Error logging out.');
        }
    });
}
