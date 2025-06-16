var email = "";
var shown = false;
var label;
var link;
var links_div;
var toggleEmail = function (e) {
    e.preventDefault();
    if (shown) {
        label.textContent = "*********";
        link.textContent = "Show";
    }
    else {
        label.textContent = email;
        link.textContent = "Hide";
    }
    shown = !shown;
};
window.onload = function () {
    var _a;
    label = document.getElementById("email_label");
    link = document.getElementById("toggle_email");
    links_div = document.getElementById("links_div");
    email = (_a = label.dataset.email) !== null && _a !== void 0 ? _a : "";
    var linksDataStr = links_div.dataset.links;
    if (!linksDataStr) {
        return;
    }
    var linksData = [];
    try {
        linksData = JSON.parse(linksDataStr);
    }
    catch (e) {
        console.error("Failed to parse linksData:", e);
    }
    // Create table
    var table = document.createElement("table");
    table.style.width = "100%";
    table.style.border = "1px solid #000000";
    // Table header
    var header = table.createTHead();
    var headerRow = header.insertRow();
    ["Shortened URL", "Redirects to", "Visits", "Created", ""].forEach(function (text) {
        var th = document.createElement("th");
        th.textContent = text;
        headerRow.appendChild(th);
    });
    // Table body
    var tbody = table.createTBody();
    linksData.forEach(function (row) {
        var tr = tbody.insertRow();
        var shortCell = tr.insertCell();
        var shortLink = document.createElement("a");
        shortLink.href = "/".concat(row[0]);
        shortLink.textContent = "".concat(window.location.origin, "/").concat(row[0]);
        shortLink.target = "_blank";
        shortCell.appendChild(shortLink);
        // Redirects to
        var urlCell = tr.insertCell();
        var urlLink = document.createElement("a");
        urlLink.href = urlLink.textContent = "".concat(row[1]);
        urlLink.target = "_blank";
        urlCell.appendChild(urlLink);
        // Visits
        var visitsCell = tr.insertCell();
        visitsCell.textContent = row[2];
        // Created
        var createdCell = tr.insertCell();
        createdCell.textContent = row[3];
        // Delete link
        var deleteCell = tr.insertCell();
        var deleteForm = document.createElement("form");
        deleteForm.action = "/delete/".concat(row[0]);
        deleteForm.method = "POST";
        var deleteButton = document.createElement("input");
        deleteButton.type = "submit";
        deleteButton.value = "Delete";
        deleteButton.onclick = function (e) {
            if (!confirm("Are you sure you want to delete this link?")) {
                e.preventDefault();
            }
        };
        deleteForm.appendChild(deleteButton);
        deleteCell.appendChild(deleteForm);
    });
    links_div.appendChild(table);
};
