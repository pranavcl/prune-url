let search_links_div: HTMLDivElement;

window.onload = () => {
    search_links_div = document.getElementById("search-links-div") as HTMLDivElement;

    let linksDataStr = search_links_div.dataset.links;

    if (!linksDataStr) {
        return;
    }

    let linksData: any[] = [];
    try {
        linksData = JSON.parse(linksDataStr);
    } catch (e) {
        console.error("Failed to parse linksData:", e);
    }

    const table = document.createElement("table");
    table.style.width = "100%";
    table.style.border = "1px solid #000000";

    const header = table.createTHead();
    const headerRow = header.insertRow();
    ["Made by", "Short URL", "Redirect", "Visits", "Created"].forEach(text => {
        const th = document.createElement("th");
        th.textContent = text;
        headerRow.appendChild(th);
    });

    const tbody = table.createTBody();

    linksData.forEach((row) => {
        const tr = tbody.insertRow();
        
        const madeByCell = tr.insertCell();
        const madeByParagraph = document.createElement("p");
        madeByParagraph.textContent = row[0];
        madeByCell.appendChild(madeByParagraph);
        
        const shortCell = tr.insertCell();
        const shortLink = document.createElement("a");

        shortLink.href = `/${row[1]}`;
        shortLink.textContent = `${window.location.origin}/${row[1]}`;
        shortLink.target = "_blank";
        shortCell.appendChild(shortLink);

        // Redirects to
        const urlCell = tr.insertCell();
        const urlLink = document.createElement("a");

        urlLink.href = urlLink.textContent = `${row[2]}`;
        urlLink.target = "_blank";
        urlCell.appendChild(urlLink);

        // Visits
        const visitsCell = tr.insertCell();
        visitsCell.textContent = row[3];

        // Created
        const createdCell = tr.insertCell();
        createdCell.textContent = row[4];
    });

    search_links_div.appendChild(table);
}