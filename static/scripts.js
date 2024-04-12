// Define the available books array
let available = {{ books_name | tojson }}; // Remove the quotes

// Convert available to an array
available = JSON.parse(available);

// Select elements
const inputbox = document.querySelector("#search-box");
const resultbox = document.querySelector(".result-box");

// Function to search books
const searchBooks = () => {
    let input = inputbox.value.trim().toLowerCase(); // Trim and convert input to lowercase

    if (input.length) {
        let result = available.filter(book => book.toLowerCase().includes(input)); // Filter books based on input

        console.log(result);
        updateResultBox(result); // Update the result box with filtered books
    } else {
        updateResultBox([]);
    }
}

// Function to update the result box
function updateResultBox(searchResults) {
    resultbox.innerHTML = ''; // Clear previous results
    searchResults.forEach(item => {
        const resultItem = document.createElement('div');
        resultItem.classList.add('result-item');
        resultItem.textContent = item;
        resultbox.appendChild(resultItem); // Append each result item to the result box
    });
}
