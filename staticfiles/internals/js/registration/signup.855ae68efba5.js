$(function () {
    let username_error_msg = $("#username_error_msg");
    let email_error_msg = $("#email_error_msg");
    let password_error_msg = $("#password_error_msg");
    let password_confirm_error_msg = $("#password_confirm_error_msg");
    let form_username = $("#form_username");
    let form_email = $("#form_email");
    let submit_error = $("#submit_error");
    let form_password = $("#form_password");
    let form_password_confirm = $("#form_password_confirm");

    submit_error.hide();
    //declaration of boolean variables to check if there are error or no in each field of the form before sending it 
    let error_username = false;
    let error_email = false;
    let error_password = false;
    let error_password_confirm = false;

    let border_bottom_error = "2px solid #F90A0A";
    let border_bottom_success = "2px solid #34F458";

    form_username.focus(function () {
        form_username.css("border-bottom", '');
    });
    form_username.focusout(function () {
        check_username();
    });

    form_email.focus(function () {
        form_email.css("border-bottom", '');
    });
    form_email.focusout(function () {
        check_email();
    });

    form_password.focus(function () {
        form_password.css("border-bottom", '');
    });
    form_password.focusout(function () {
        check_password();
    });

    form_password_confirm.focus(function () {
        form_password_confirm.css("border-bottom", '');
    });
    form_password_confirm.focusout(function () {
        check_password_confirm();
    });


    //declaration of functions which check if each field respect the contrains 
    function check_username() {
        var pattern = /^[a-zA-Z0-9]{5,}$/;
        var form_username = $("#form_username");
        var username = form_username.val();
        if (pattern.test(username) && username !== '') {
            username_error_msg.hide();
            form_username.css("border-bottom", border_bottom_success);
        }
        else {
            username_error_msg.html("Le nom d'utilisateur doit avoir au moins 5 caracteres")
                .show();
            form_username.css("border-bottom", border_bottom_error);
            error_username = true;
        }
    }

    function check_email() {

        var email = form_email.val();
        if (isValidEmailAddress(email)) {
            email_error_msg.hide();
            form_email.css("border-bottom", border_bottom_success);
        }
        else {
            email_error_msg.html("L'adresse email n'est pas valide")
                .show();
            form_email.css("border-bottom", border_bottom_error);
            error_email = true;
        }
    }

    function check_password() {
        var password_length = form_password.val().length;
        if (password_length < 5) {
            password_error_msg.html("Le mot de passe doit avoir au minimum 5 caracteres")
                .show();
            form_password.css("border-bottom", border_bottom_error);
            error_password = true;
        }
        else {
            password_error_msg.hide();
            form_password.css("border-bottom", border_bottom_success);
        }
    }

    function check_password_confirm() {
        var password = form_password.val();
        var password_confirm = form_password_confirm.val();
        if (password !== '' && password === password_confirm) {
            password_confirm_error_msg.hide();
            form_password_confirm.css("border-bottom", border_bottom_success);
        }
        else {
            password_confirm_error_msg.html("Les deux mot de passe ne sont pas identiques")
                .show();
            form_password_confirm.css("border-bottom", border_bottom_error);
            error_password_confirm = true;
        }
    }

    //The function which check if there are error or no when the user want to submit the form to send or no the request
    $("#registration_form").submit(function (e) {
        error_email = false;
        error_password = false;
        error_username = false;
        error_password_confirm = false;

        check_email();
        check_password();
        check_username();
        check_password_confirm();

        if (error_email === false && error_password === false && error_password_confirm === false
            && error_username === false) {
            return true;
        }
        else {
            submit_error.show();
            e.preventDefault();
        }
    });

    function isValidEmailAddress(emailAddress) {
        var pattern = /^([a-z\d!#$%&'*+\-\/=?^_`{|}~\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]+(\.[a-z\d!#$%&'*+\-\/=?^_`{|}~\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]+)*|"((([ \t]*\r\n)?[ \t]+)?([\x01-\x08\x0b\x0c\x0e-\x1f\x7f\x21\x23-\x5b\x5d-\x7e\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]|\\[\x01-\x09\x0b\x0c\x0d-\x7f\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]))*(([ \t]*\r\n)?[ \t]+)?")@(([a-z\d\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]|[a-z\d\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF][a-z\d\-._~\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]*[a-z\d\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])\.)+([a-z\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]|[a-z\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF][a-z\d\-._~\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]*[a-z\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])\.?$/i;
        return pattern.test(emailAddress);
    }

});
