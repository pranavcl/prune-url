"use strict";
let users_div;
window.onload = () => {
    users_div = document.getElementById("users-div");
    let usersDataStr = users_div.dataset.users;
    if (!usersDataStr) {
        return;
    }
    let usersData = [];
    try {
        usersData = JSON.parse(usersDataStr);
    }
    catch (e) {
        console.error("Failed to parse linksData:", e);
    }
    const table = document.createElement("table");
    table.style.width = "100%";
    table.style.border = "1px solid #000000";
    const header = table.createTHead();
    const headerRow = header.insertRow();
    ["Email", "Role", "Links Made", "Links Limit", "Date Created", "Total Visits"].forEach(text => {
        const th = document.createElement("th");
        th.textContent = text;
        headerRow.appendChild(th);
    });
    const tbody = table.createTBody();
    usersData.forEach((row) => {
        const tr = tbody.insertRow();
        for (let i = 0; i < row.length; i++) {
            const cell = tr.insertCell();
            const cell_paragraph = document.createElement("p");
            cell_paragraph.textContent = row[i];
            cell.appendChild(cell_paragraph);
        }
    });
    users_div.appendChild(table);
};
