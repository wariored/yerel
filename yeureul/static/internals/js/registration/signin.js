$(function(){
         valideName = false;
         validePasswd = false;
    
    
        $('#id_email_username').on({
            mouseenter : function(){ 
                        $('form span')[0].textContent = "*";                       
                    },
            mouseleave: function(){ 
                        var email = $('#id_email_username').val();
                        if (email.indexOf("@") == -1){
                            $('form span')[0].textContent = ": L'adresse mail ne semble pas etre correct.";
                            valideName= false;
                        }else{
                            $('form span')[0].textContent = "*";
                            valideName= true;
                            }
                    }
        });
        $('#id_password').on({
            mouseenter : function(){ 
                                $('form span')[1].textContent = "*";                       
                            },
            mouseleave: function(){ 
                        var password = $('#id_password').val();
                        if (password.length < 5){
                            $('form span')[1].textContent = ": Pou plus de securite, le mot de passe doit contenir au minimum 5 caracteres";
                            validePasswd= false;
                        }else{
                            $('form span')[1].textContent = "*";
                            validePasswd= true;
                            }
                    }
        });

        $('form').submit(function(e){
                               if((valideName && validePasswd)  === false){
                                   e.preventDefault();
                               }
                                    }
    
        );
        
    })