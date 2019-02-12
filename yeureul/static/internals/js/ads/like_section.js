$(document).ready(function(e){
    alert('{{ csrf_token }}');
    $(document).on('click', "#like" , function(e){
        e.preventDefault()  ;
        var pk = $(this).attr('value'); 
        $.ajax({
            type : 'POST', 
            url : '{% url "ads:like_post"   %}' ,
            headers : {'X-CSRFToken' : '{{ csrf_token }}' } ,
            data : {'id':pk  }  , // , 'csrfmiddlewaretoken' : '{{ csrf_token }}' } ,
            dataType :'json', 
            success : function(response){
                alert("reussit") ; 
                $('#like_section').html(response['form']) 
                console.log($('#like_section').html(response['form'])); 
            }  ,
            error : function(rs,e){
                alert("erreur ") ;     
                console.log(rs.responseText)     
            }
        }) ; 
    }) ; 
}) ; 