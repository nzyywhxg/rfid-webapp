document.addEventListener('DOMContentLoaded', () => {
    const textarea = document.querySelector('#mainTXT');
    const outputContainer = document.querySelector('pre');
    const searchBtn = document.querySelector('#searchBtn');
    const searchBarContainer = document.querySelector('#searchBarContainer');
    if (textarea) {
        textarea.addEventListener('input', function() {
            const formData = new FormData();
            formData.append('user_input', textarea.value);
            formData.append('action', 'update_text');  // Specify the action for the AJAX request

            fetch('/update', {
                method: 'POST',
                body: formData
            })
            .then(response => response.text())
            .then(data => {
                console.log("AJAX Response Data:", data);
                outputContainer.innerHTML = data.replace(/\n/g, '<br>');  // Update the page content with the response
            })
            .catch(error => console.error('Detected Error:', error));
        });
        // handle search buttone functions 
        searchBtn.addEventListener('click', function() {
            // Prevent the form from submitting
            event.preventDefault();

            // Create a new input element for search
            if (!document.querySelector('input[name="search_text"]')) {
                const searchBar = document.createElement('input');
                searchBar.setAttribute('type', 'text');
                searchBar.setAttribute('name', 'search_text');
                searchBar.setAttribute('placeholder', 'Search for items...');
                searchBar.style.width = '100%';
                searchBarContainer.appendChild(searchBar);

                searchBar.addEventListener('input', function() {
                    const formData = new FormData();
                    formData.append('search_text', searchBar.value);

                    fetch('/search', {
                        method: 'POST',
                        body: formData
                    })
                    .then(response => response.text())
                    .then(data => { outputContainer.innerHTML = data.replace(/\n/g, '<br>');  
                        // Update with search result
                    })
                    .catch(error => console.error('Error:', error));
                });
            }
        });

    }

});

