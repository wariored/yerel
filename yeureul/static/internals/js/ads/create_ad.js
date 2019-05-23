$(function () {
    let title_error_msg = $("#title_error_msg");
    let desc_error_msg = $("#desc_error_msg");
    let name_error_msg = $("#name_error_msg");
    let email_error_msg = $("#email_error_msg");
    let phone_error_msg = $("#phone_error_msg");
    let submit_error = $("#submit_error");
    let check_user = document.getElementById('form_name'); 
    let title = document.getElementById('form_title'); 

    submit_error.hide()

    let form_title = $("#form_title");
    let form_desc = $("#form_desc");
    let form_name = $("#form_name");
    let form_email = $("#form_email");
    let form_phone = $("#form_phone");

    //declaration of boolean variables to check if there are error or no in each field of the form before sending it 
    let error_title = false;
    let error_desc = false;
    let error_name = false;
    let error_email = false;
    let error_phone = false;

    let border_bottom_error = "2px solid #F90A0A";
    let border_bottom_success = "2px solid #34F458";

    form_title.focus(function () {
        form_title.css("border-bottom", '');
    });
    form_title.focusout(function () {
        check_title();
    });

    form_desc.focus(function () {
        form_desc.css("border-bottom", '');
    });
    form_desc.focusout(function () {
        check_desc();
    });

    if(check_user){
        form_email.focus(function () {
            form_email.css("border-bottom", '');
        });
        form_email.focusout(function () {
            check_email();
        });
    
        form_name.focus(function () {
            form_name.css("border-bottom", '');
        });
        form_name.focusout(function () {
            check_name();
        });
    
        form_phone.focus(function () {
            form_phone.css("border-bottom", '');
        });
        form_phone.focusout(function () {
            check_phone();
        });
    }

    //declaration of functions which check if each field respect the contrains 
    function check_title() {
        let pattern = /^[a-zA-Z0-9\s]{2,50}$/;
        let title = form_title.val();
        if (title.length >=2 && pattern.test(title)) {
            title_error_msg.hide();
            form_title.css("border-bottom", border_bottom_success);
        }
        else {
            title_error_msg.html("Le titre doit avoir plus de 2 caracteres et moins de 50 caracteres")
                .show();
            form_title.css("border-bottom", border_bottom_error);
            error_title = true;
        }
    }

    function check_email() {
        let email = form_email.val();
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

    function check_name() {
        let pattern = /^[a-zA-Z\s]{2,50}$/;
        let name = form_name.val();
        if (pattern.test(name)) {
            name_error_msg.hide();
            form_name.css("border-bottom", border_bottom_success);
        }
        else {
            name_error_msg.html("Le nom doit avoir plus de 2 caracteres et moins de 50 caracteres")
                .show();
            form_name.css("border-bottom", border_bottom_error);
            error_name = true;
        }
    }
    function check_desc() {
        let pattern = /^[a-zA-Z0-9\s]{20,2000}$/;
        let desc = form_desc.val();
        if (pattern.test(desc)) {
            desc_error_msg.hide();
            form_desc.css("border-bottom", border_bottom_success);
        }
        else {
            desc_error_msg.html("La description doit avoir plus de 20 caracteres et moins de 2000 caracteres")
                .show();
            form_desc.css("border-bottom", border_bottom_error);
            error_desc = true;
        }
    }

    function check_phone(){
        let pattern = /^((76)?(77)?(70)?(33)?(78)?)+\d{7}$/;
        let number = form_phone.val()
        if(number.length == 9 && pattern.test(number)){
            phone_error_msg.hide()
            form_phone.css("border-bottom", border_bottom_success)
        }else{
            phone_error_msg.html("Le numero n'est pas correct").show();
            form_phone.css("border-bottom", border_bottom_error);
            error_phone = true;
        }
    }


    //The function which check if there are error or no when the user want to submit the form to send or no the request
    $("#ad_form").submit(function (e) {
        error_title = false;
        error_desc = false;
        error_name = false;
        error_email = false;
        error_phone = false;

        if(check_user){
            check_name();
            check_phone()
            check_email();
        }
        if(title){
            check_title();
        }

        check_desc();

        if (error_title === false && error_desc === false && error_name === false
            && error_email === false && error_phone === false) {
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
