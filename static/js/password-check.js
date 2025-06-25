document.addEventListener("DOMContentLoaded", function() {
    const passwordInput = document.getElementById("password");
    const reqLength = document.getElementById("req-length");
    const reqUpper = document.getElementById("req-upper");
    const reqLower = document.getElementById("req-lower");
    const reqNumber = document.getElementById("req-number");

    if (!passwordInput) return;

    passwordInput.addEventListener("input", function() {
        const val = passwordInput.value;
        reqLength.style.display = val.length >= 5 ? "none" : "list-item";
        reqUpper.style.display = /[A-Z]/.test(val) ? "none" : "list-item";
        reqLower.style.display = /[a-z]/.test(val) ? "none" : "list-item";
        reqNumber.style.display = /[0-9]/.test(val) ? "none" : "list-item";
    });
});