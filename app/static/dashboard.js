var email = "";
var shown = false;
var label;
var link;
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
    email = (_a = label.dataset.email) !== null && _a !== void 0 ? _a : "";
};
