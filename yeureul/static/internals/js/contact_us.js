// import {} from 'registration/signup.js' ; 

$(function(){
    let name_error_msg = $("#name_error_msg") ; 
    let email_error_msg = $("#email_error_msg") ; 
    let message_error_msg = $("#message_error_msg") ; 

    let form_name = $("#form_name");
    let form_email = $("#form_email");
    let form_message = $("#form_message") ; 
    let submit_error = $("#submit_error");

    submit_error.hide();

    let error_name = false;
    let error_email = false;
    let error_message = false;

    let border_bottom_error = "2px solid #F90A0A";
    let border_bottom_success = "2px solid #34F458";

    form_name.focus(function () {
        form_name.css("border-bottom", '');
    });
    form_name.focusout(function () {
        check_name();
    });

    form_email.focus(function () {
        form_email.css("border-bottom", '');
    });
    form_email.focusout(function () {
        check_email();
    });

    form_message.focus(function(){
        form_message.css("border-bottom" , "") ; 
    });

    form_message.focusout(function(){
        check_message() ; 
    });

    function check_name() {
        let pattern = /^([a-zA-Z]{2,})+(\s{1}([a-zA-Z]){2,})*$/ ; 
        // let pattern = /^[a-z]+([ \-']?[a-z]+[ \-']?[a-z]+[ \-']?)[a-z]+$/gi;
        let form_name = $("#form_name");
        let name = form_name.val();
        if (pattern.test(name) && name !== '') {
            name_error_msg.hide();
            form_name.css("border-bottom", border_bottom_success);
        }
        else {
            name_error_msg.html("Le nom n'est pas correcte")
                .show();
            form_name.css("border-bottom", border_bottom_error);
            error_name = true;
        }
    }

    // function check_email() {
    //     let pattern = /^([\w-\.]+@([\w-]+\.)+[\w-]{2,4})?$/;
    //     let email = form_email.val();
    //     if (pattern.test(email) && email !== '') {
    //         email_error_msg.hide();
    //         form_email.css("border-bottom", border_bottom_success);
    //     }
    //     else {
    //         email_error_msg.html("L'adresse email n'est pas valide")
    //             .show();
    //         form_email.css("border-bottom", border_bottom_error);
    //         error_email = true;
    //     }
    // }

    function check_message(){
        let pattern = /\w/ ;
        let form_message = $("#form_message") ; 
        let message = form_message.val() ; 
        if(pattern.test(message)){
            message_error_msg.hide() ; 
            form_message.css("border-bottom" , border_bottom_success);
        }else{
            message_error_msg.html("Le message ne doit pas etre vide");
            message_error_msg.show() ; 
            form_message.css("border-bottom" , border_bottom_error) ; 
            error_message = true  ; 
        }

    }
    $("#contactForm").submit(function(e){
        error_name = false;
        error_email = false;
        error_message = false;

        check_name();
        check_email();
        check_message();

        if (error_name === false && error_email === false && error_message === false)
        {
            return true;
        }
        else {
            submit_error.show();
            e.preventDefault();
        }
    });

});