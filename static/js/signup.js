document.addEventListener('DOMContentLoaded', function() {
    var passwordInput = document.getElementById('password');
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            var pwd = this.value;
            var checks = [
                { id: 'req-length',   valid: pwd.length >= 8 },
                { id: 'req-upper',    valid: /[A-Z]/.test(pwd) },
                { id: 'req-lower',    valid: /[a-z]/.test(pwd) },
                { id: 'req-number',   valid: /[0-9]/.test(pwd) },
                { id: 'req-special',  valid: /[!@#$%^&*(),.?":{}|<>]/.test(pwd) }
            ];
            checks.forEach(function(check) {
                var el = document.getElementById(check.id);
                if (el) {
                    el.style.display = check.valid ? 'none' : '';
                }
            });
        });
    }

    setTimeout(function() {
        var flashMessages = document.getElementById('flash-messages');
        if (flashMessages) {
            flashMessages.style.display = 'none';
        }
    }, 3000);
});