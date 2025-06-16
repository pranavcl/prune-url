let email: string = "";
let shown = false;

let label: HTMLParagraphElement;
let link: HTMLAnchorElement;
let links_div: HTMLDivElement;

const toggleEmail = (e: Event) => {
    e.preventDefault();

    if(shown) {
        label.textContent = "*********";
        link.textContent = "Show";
    } else {
        label.textContent = email;
        link.textContent = "Hide";
    }

    shown = !shown;
}

window.onload = () => {   
    label = document.getElementById("email_label") as HTMLParagraphElement;
    link = document.getElementById("toggle_email") as HTMLAnchorElement;
    links_div = document.getElementById("links_div") as HTMLDivElement;
     
    email = label.dataset.email ?? "";
    
    let linksDataStr = links_div.dataset.links;

    if (!linksDataStr) {
        return;
    }

    let linksData: any[] = [];
    try {
        linksData = JSON.parse(linksDataStr);
    } catch (e) {
        console.error("Failed to parse linksData:", e);
    }

    // Create table
    const table = document.createElement("table");
    table.style.width = "100%";
    table.style.border = "1px solid #000000";

    // Table header
    const header = table.createTHead();
    const headerRow = header.insertRow();
    ["Shortened URL", "Redirects to", "Visits", "Created", ""].forEach(text => {
        const th = document.createElement("th");
        th.textContent = text;
        headerRow.appendChild(th);
    });

    // Table body
    const tbody = table.createTBody();
    linksData.forEach(row => {
        const tr = tbody.insertRow();
        
        const shortCell = tr.insertCell();
        const shortLink = document.createElement("a");

        shortLink.href = `/${row[0]}`;
        shortLink.textContent = `${window.location.origin}/${row[0]}`;
        shortLink.target = "_blank";
        shortCell.appendChild(shortLink);

        // Redirects to
        const urlCell = tr.insertCell();
        const urlLink = document.createElement("a");

        urlLink.href = urlLink.textContent = `${row[1]}`;
        urlLink.target = "_blank";
        urlCell.appendChild(urlLink);

        // Visits
        const visitsCell = tr.insertCell();
        visitsCell.textContent = row[2];

        // Created
        const createdCell = tr.insertCell();
        createdCell.textContent = row[3];

        // Delete link
        const deleteCell = tr.insertCell();
        const deleteForm = document.createElement("form");
        deleteForm.action=`/delete/${row[0]}`;
        deleteForm.method="POST";
        const deleteButton = document.createElement("input");
        deleteButton.type = "submit";
        deleteButton.value = "Delete";
        deleteButton.onclick = (e) => {
            if (!confirm("Are you sure you want to delete this link?")) {
                e.preventDefault();
            }
        };
        deleteForm.appendChild(deleteButton);
        deleteCell.appendChild(deleteForm);
    });

    links_div.appendChild(table);
    
}