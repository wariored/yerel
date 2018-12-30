$(function () {
    let username_email = $('#id_email_username');
    let password = $('#id_password');

    let username_email_error_msg = $('#username_email_error_msg');
    let password_error_msg = $('#password_error_msg');

    let username_email_error = false;
    let password_error = false;

    username_email.prop('required', false);
    password.prop('required', false);

    username_email.focus(function () {
        username_email_error_msg.html("");
    });
    username_email.focusout(function () {
        check_username_email();

    });

    password.focus(function () {
        password_error_msg.html("");
    });
    password.focusout(function () {
        check_password();
    });


    function check_username_email() {
        var username_email_val = username_email.val();
        if (username_email_val === '') {
            username_email_error = true;
            username_email_error_msg.html("Veuillez entrer un nom d'utilisateur ou adresse mail");
        }
    }


    function check_password() {
        var password_val = password.val();
        if (password_val.length < 5) {
            password_error_msg.html('Il est recommandé que le mot de passe soit au minimum 5 caractères. ' +
                "Veuillez le changer une fois connecté si tel n''est pas le cas");
            password_error_msg.removeClass('text-danger')
                .addClass('text-warning')
        }
        if (password_val === '') {
            password_error = true;
            password_error_msg.html("Veuillez entrer un mot de passe");
            password_error_msg.removeClass('text-warning')
                .addClass('text-danger')
        }
    }


    $("#login_form").submit(function (e) {
        username_email_error = false;
        password_error = false;

        check_username_email();
        check_password();

        if (username_email_error === true || password_error === true) {
            e.preventDefault();
        }
    });

});