$(function () {
    //Variable that handle the error showing when there is one 
    let fname_error_msg = $("#fname_error_msg");
    let lname_error_msg = $("#lname_error_msg");
    let address_error_msg = $("#address_error_msg");
    let phone_error_msg = $("#phone_error_msg");
    let old_password_error_msg = $("#old_password_error_msg");
    let password_error_msg = $("#password_error_msg");
    let password_confirm_error_msg = $("#password_confirm_error_msg");
    let submit_error = $("#submit_error");

    submit_error.hide();

    //variable of each form to check if the value is correct
    let form_fname = $("#form_fname");
    let form_lname = $("#form_lname");
    let form_address = $("#form_address");
    let form_phone = $("#form_phone");
    let form_old_password = $("#form_old_password");
    let form_password = $("#form_password");
    let form_password_confirm = $("#form_password_confirm");


    //declaration of boolean letiables to check if there are error or no in each field of the form before sending it 
    let error_fname = false;
    let error_lname = false;
    let error_address = false;
    let error_old_password = false;
    let error_password = false;
    let error_password_confirm = false;
    let error_phone = false;

    let border_bottom_error = "2px solid #F90A0A";
    let border_bottom_success = "2px solid #34F458";
    
    form_lname.focus(function () {
        form_lname.css("border-bottom", '');
    });
    form_lname.focusout(function () {
        check_lname();
    });

    form_fname.focus(function () {
        form_fname.css("border-bottom", '');
    });
    form_fname.focusout(function () {
        check_fname();
    });

    form_address.focus(function () {
        form_address.css("border-bottom", '');
    });
    form_address.focusout(function () {
        if(form_address.val()){
        check_address();
        }else{
        address_error_msg.hide();  
        }
    });

    form_old_password.focus( function() {
        form_old_password.css("border-bottom", '');
    });
    form_old_password.focusout(function () {
        if(form_old_password.val()){
            check_old_password();
        }else{
        old_password_error_msg.hide();  
        }
    });

    form_password.focus( function() {
        form_fname.css("border-bottom", '');
    });
    form_password.focusout(function () {
        if(form_password.val()){
            check_password();
        }else{
        password_error_msg.hide();  
        }
    });

    form_password_confirm.focus( function() {
        form_fname.css("border-bottom", '');
    });
    form_password_confirm.focusout(function () {
        if(form_password_confirm.val()){
            check_password_confirm();
        }else{
        password_confirm_error_msg.hide();  
        }
    });
    
    //check if  a given address is correct
    function check_address() {
        let address = form_address.val();
        if (address.length >= 2 && address.length <= 50) {
            address_error_msg.hide();
            form_address.css("border-bottom", border_bottom_success);
        }
        else {
            address_error_msg.html("L'adresse doit avoir plus de 2 caractères ")
                .show();
            form_address.css("border-bottom", border_bottom_error);
            error_address = true;
        }
    }

    //check if the first name is correct before sending the form 
    function check_fname() {
        let fname = form_fname.val();
        if (fname.length >= 2 && fname.length <= 50) {
            fname_error_msg.hide();
            form_fname.css("border-bottom", border_bottom_success);
        }
        else {
            fname_error_msg.html("Le prenom doit avoir entre 2 et 50  caractères")
                .show();
            form_fname.css("border-bottom", border_bottom_error);
            error_fname = true;
        }
    }

    //check is the last name js correct
    function check_lname() {
        let lname = form_lname.val();
        if (lname.length >= 2 && lname.length <= 50) {
            lname_error_msg.hide();
            form_lname.css("border-bottom", border_bottom_success);
        }
        else {
            lname_error_msg.html("Le nom doit avoir entre 2 et 50  caractères")
                .show();
            form_lname.css("border-bottom", border_bottom_error);
            error_lname = true;
        }
    }

    //check if the cell phone is correct 
    function check_phone() {
        let pattern = /^((76)?(77)?(70)?(33)?(78)?)+\d{7}$/;
        let number = form_phone.val();
        if (number.length === 9 && pattern.test(number)) {
            phone_error_msg.hide();
            form_phone.css("border-bottom", border_bottom_success);
        } else {
            phone_error_msg.html("Le numéro n'est pas correct").show();
            form_phone.css("border-bottom", border_bottom_error);
            error_phone = true;
        }
    }

    //check if the old passwor respect the needed form
    function check_old_password() {
        let old_password_length = form_old_password.val().length;
        if (old_password_length < 5) {
            old_password_error_msg.html("Le mot de passe doit avoir au minimum 5 caracteres")
                .show();
            form_old_password.css("border-bottom", border_bottom_error);
            error_old_password = true;
        }
        else {
            old_password_error_msg.hide();
            form_old_password.css("border-bottom", border_bottom_success);
        }
    }
    function check_password() {
        let password_length = form_password.val().length;
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
        let password = form_password.val();
        let password_confirm = form_password_confirm.val();
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
    $("#settings").submit(function (e) {
        error_address = false;
        error_fname = false;
        error_lname = false;
        error_phone = false;
        error_old_password = false;
        error_password = false;
        error_password_confirm = false;

        check_fname();
        check_lname();
        check_phone();
        if(form_address.val()){
            check_address();
        }
        
        if(form_old_password.val()){
            check_old_password();
        }
        if(form_password.val()){
            check_password();
        }else if (form_old_password.val()){
            check_password();
        }

        if(form_password_confirm.val()){
            check_password_confirm();
        }else if (form_old_password.val() || form_password.val()){
            check_password_confirm();
        }

        if (error_address === false && error_fname === false &&
            error_lname === false && error_old_password === false &&
            error_password === false && error_password_confirm === false &&
            error_phone === false) {
            return true;
        }
        else {
            submit_error.show();
            e.preventDefault();
        }
    });
});
