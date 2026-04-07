// Simple search function to filter table rows
function filterTable() {
    // Get the input value and convert to lowercase
    let input = document.getElementById("searchInput");
    let filter = input.value.toLowerCase();
    
    // Get the table and its rows
    let table = document.getElementById("dataTable");
    let tr = table.getElementsByTagName("tr");

    // Loop through all table rows (skipping the header row)
    for (let i = 1; i < tr.length; i++) {
        let textValue = tr[i].textContent || tr[i].innerText;
        // If the row text matches the search, show it; otherwise hide it
        if (textValue.toLowerCase().indexOf(filter) > -1) {
            tr[i].style.display = "";
        } else {
            tr[i].style.display = "none";
        }
    }
}