$(document).ready(function(e){
    $(document).on('click', "#like" , function(e){
        e.preventDefault()  ;
        var pk = $(this).attr('value');  
        $.ajax({
            type : 'POST', 
            url : '{% url "like_post"  %}' ,
            data : {'id':pk ,'csrfmiddlewaretoken' : '{{ csrf_token }}' } ,
            dataType :'json',
            success : function(response){
                $('#like_section').html(response['form']) 
                console.log($('#like_section').html(response['form'])); 
            }  ,
            error : function(rs,e){
               console.log(rs.responseText)     
            }
        }) ; 
    }) ; 
}) ; 