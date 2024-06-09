/** obtaining the button */
const button = document.getElementById("menubutton");

/** call OpenMenu when the button is clicked */
button.addEventListener('click', OpenMenu);

/** using this to obtain the menu container */
const menu = document.getElementById("menu");

/* apply the class showmenu to menu when the button is clicked */
function OpenMenu() 
{
    menu.classList.toggle("showmenu"); 
}

/* getting the close button */
const close = document.getElementById("close");

/* call CloseMenu when close is clicked */
close.addEventListener('click', CloseMenu);
function CloseMenu()
{
    menu.classList.toggle("showmenu");
}
