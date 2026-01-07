// Function that runs once the window is fully loaded
window.onload = function() {
    // Attempt to retrieve the API base URL from the local storage
    const savedBaseUrl = localStorage.getItem('apiBaseUrl');
    // If a base URL is found in local storage, load the posts
    if (savedBaseUrl) {
        document.getElementById('api-base-url').value = savedBaseUrl;
        loadPosts();
    }
}

// Function to fetch all the posts from the API and display them on the page
function loadPosts() {
    const baseUrl = document.getElementById('api-base-url').value;
    localStorage.setItem('apiBaseUrl', baseUrl);

    fetch(baseUrl + '/api/posts')  // include '/api'
    .then(response => response.json())
    .then(data => {
        const postContainer = document.getElementById('post-container');
        postContainer.innerHTML = '';

        data.forEach(post => {
            const postDiv = document.createElement('div');
            postDiv.className = 'post';
            postDiv.innerHTML = `
                <h2>${post.title}</h2>
                <p>${post.content}</p>
                <p><em>By ${post.author} on ${post.date}</em></p>
                <button onclick="deletePost(${post.id})">Delete</button>
            `;
            postContainer.appendChild(postDiv);
        });
    })
    .catch(error => console.error('Error:', error));
}


// Function to send a POST request to the API to add a new post
function addPost() {
    const baseUrl = document.getElementById('api-base-url').value;
    const titleInput = document.getElementById('post-title');
    const contentInput = document.getElementById('post-content');
    const authorInput = document.getElementById('post-author');

    // Construct the post object
    const postData = {
        title: titleInput.value,
        content: contentInput.value,
        author: authorInput.value
    };

    fetch(baseUrl + '/api/posts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(postData)
    })
    .then(response => {
        if (!response.ok) throw new Error('Failed to add post');

        // ✅ Clear input fields AFTER successful add
        titleInput.value = '';
        contentInput.value = '';
        authorInput.value = '';

        // ✅ Reload posts
        loadPosts();
    })
    .catch(error => console.error('Error:', error));
}


// Function to send a DELETE request to the API to delete a post
function deletePost(postId) {
    const baseUrl = document.getElementById('api-base-url').value;

    fetch(`${baseUrl}/api/posts/${postId}`, {
        method: 'DELETE'
    })
    .then(response => {
        if (response.ok) {
            console.log('Post deleted:', postId);
            loadPosts();
        } else {
            console.error('Failed to delete post', postId);
        }
    })
    .catch(error => console.error('Error:', error));
}