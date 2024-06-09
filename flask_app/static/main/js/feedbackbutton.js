//Const variables for these ids on my page
const feedbackbutton = document.getElementById("feedbackbutton");
const feedbackform = document.getElementById("feedbackform");

//An event listener for the button
feedbackbutton.addEventListener('click', OpenFeedback);

//When the button is clicked, and the display is flex, it should change the display to none
//if display is none, change display to flex when button is clicked
function OpenFeedback()
{
    if (feedbackform.style.display === 'flex')
    {
        feedbackform.style.display = 'none';
    }
    else
    {
        feedbackform.style.display = 'flex';
    }
}




