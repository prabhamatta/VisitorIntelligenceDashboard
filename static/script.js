document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("uploadBtn").addEventListener("click", uploadFile);
    document.getElementById("filterBtn").addEventListener("click", filterData);
});

function uploadFile() {
    let fileInput = document.getElementById("fileInput").files[0];
    let formData = new FormData();
    formData.append("file", fileInput);
    fetch("/upload", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        populateFilters(data);
        alert(data.message);
        filterBtn.enabled = true;
    })
    .catch(error => console.error("Error:", error));
}

function populateFilters(data) {
    populateDropdown("browser", data.browsers || []);
    populateDropdown("os", data.os || []);
    populateDropdown("device", data.devices || []);
    populateDropdown("domain", data.domains || []);
    populateDropdown("page", data.pages || []);
    populateDropdown("referral", data.referrals || []);

}

function populateDropdown(id, values) {
    let select = document.getElementById(id);
    select.innerHTML = '<option value="All">All</option>';
    values.forEach(value => {
        let option = document.createElement("option");
        option.value = value;
        option.textContent = value;
        select.appendChild(option);
    });
}

function filterData() {
    let filters = {
        browser: document.getElementById("browser").value,
        os: document.getElementById("os").value,
        device: document.getElementById("device").value,
        domain: document.getElementById("domain").value,
        page: document.getElementById("page").value,
        referral: document.getElementById("referral").value

    };

    console.log("Filters applied:", filters); // Debugging output

    fetch("/filter", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(filters)
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("data-table").textContent = JSON.stringify(data, null, 2);
    })
    .catch(error => console.error("Error:", error));
}

 // Handle reset button
 resetButton.addEventListener('click', function() {
    // Clear all input fields
    const inputs = filterForm.querySelectorAll('.filter-input');
    inputs.forEach(input => {
        input.value = '';
    });
    
    // Trigger filter with empty values to reset the display
    filterForm.dispatchEvent(new Event('submit'));
});
