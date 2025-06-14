let email: string = "";
let shown = false;

let label: HTMLParagraphElement;
let link: HTMLAnchorElement;

const toggleEmail = (e) => {
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
     
    email = label.dataset.email ?? "";
}