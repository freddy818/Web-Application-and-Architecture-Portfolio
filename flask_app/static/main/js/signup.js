const signupbutton = document.getElementById("signupbutton");

signupbutton.addEventListener('click', validateSignUp);

let count = 0;
/** something givem, slightly edited so that it can take different emails and passwords */
function validateSignUp()
{
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    // package data in a JSON object
    var data_d = {'email': email, 'password': password}
    // console.log('data_d', data_d)

    // SEND DATA TO SERVER VIA jQuery.ajax({})
    jQuery.ajax({
        url: "/process_sign_up",
        data: data_d,
        type: "POST",
        success:function(retruned_data){
              retruned_data = JSON.parse(retruned_data);
              if (retruned_data['success'] !== 1)
              {
                window.location.href = "/signup";
              }
              else
              {
                window.location.href = "/signupsuccessful";

              }
            }
        
    });
}
