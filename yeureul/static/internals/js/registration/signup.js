$(function(){
    $("#username_error_msg").hide() ; 
    $("#email_error_msg").hide() ; 
    $("#password_error_msg").hide() ; 
    $("#password_confirm_error_msg").hide() ; 
    $("#submit_error").hide() ; 

    //declaration of boolean variables to check if there are error or no in each field of the form before sending it 
    var error_username = false ; 
    var error_email = false; 
    var error_password = false ; 
    var error_password_confirm = false ; 

    $("#form_username").focusout(function(){
        check_username() ; 
    }) ; 
    $("#form_email").focusout(function(){
        check_email() ; 
    }) ; 
    $("#form_password").focusout(function(){
        check_password() ; 
    }) ;
    $("#form_password_confirm").focusout(function(){
        check_password_confirm() ; 
    }) ;

    //declaration of functions which check if each field respect the contrains 
    function check_username()
    {
        var pattern = /^[a-zA-Z0-9]{5,}$/;
        var username = $("#form_username").val() ;
        if(pattern.test(username) && username !== '')
        {
            $("#username_error_msg").hide() ; 
            $("#form_username").css("border-bottom" , "2px solid #34F458") ; 
        }
        else
        {
            $("#username_error_msg").html("Le nom d'utilisateur doit avoir au moins 5 caracteres") ; 
            $("#username_error_msg").show() ; 
            $("#form_username").css("border-bottom" , "2px solid #F90A0A") ;
            error_username = true ; 
        }
    }

    function check_email()
    {
        var pattern = /^([\w-\.]+@([\w-]+\.)+[\w-]{2,4})?$/ ;
        var email = $("#form_email").val() ; 
        if (pattern.test(email) && email !== '')
        {
            $("#email_error_msg").hide() ; 
            $("#form_email").css("border-bottom" , "2px solid #34F458") ;
        }
        else
        {
            $("#email_error_msg").html("L'adresse email n'est pas valide");
            $("#email_error_msg").show() ;
            $("#form_email").css("border-bottom" , "2px solid #F90A0A") ;
            error_email = true ; 
        }

    }

    function check_password()
    {
        var password_length = $("#form_password").val().length;
        if(password_length<5)
        {
            $("#password_error_msg").html("Le mot de passe doit avoir au minimum 5 caracteres") ;
            $("#password_error_msg").show() ; 
            $("#form_password").css("border-bottom","2px solid #F90A0A") ;
            error_password = true ;
        } 
        else
        {
            $("#password_error_msg").hide() ;
            $("#form_password").css("border-bottom" , "2px solid #34F458") ;
        }
    }

    function check_password_confirm()
    {
        var password = $("#form_password").val() ; 
        var password_confirm = $("#form_password_confirm").val() ;
        if (password !=='' && password === password_confirm)
        {
            $("#password_confirm_error_msg").hide() ;
            $("#form_password_confirm").css("border-bottom" , "2px solid #34F458");
        
        }
        else
        {
            $("#password_confirm_error_msg").html("Les deux mot de passe ne sont pas identiques")
            $("#password_confirm_error_msg").show() ; 
            $("#form_password_confirm").css("border-bottom" , "2px solid #f90A0A");
            error_password_confirm = true ; 
        }
    }
    
    //The function which check if there are error or no when the user want to submit the form to send or no the request
    $("#registration_form").submit(function(){
        error_email = false ; 
        error_password = false ; 
        error_username = false  ; 
        error_password_confirm = false ; 

        check_email() ; 
        check_password() ; 
        check_username() ; 
        check_password_confirm() ; 

        if (error_email === false && error_password === false && error_password_confirm === false
            && error_username === false)
        { 
            return true ;   
        }
        else
        {
            $("#submit_error").show() ; 
            return false ; 
        }     
    }) ; 
    
}) ; 
