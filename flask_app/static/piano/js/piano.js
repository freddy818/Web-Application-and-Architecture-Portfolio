const sound = {65:"http://carolinegabriel.com/demo/js-keyboard/sounds/040.wav",
                87:"http://carolinegabriel.com/demo/js-keyboard/sounds/041.wav",
                83:"http://carolinegabriel.com/demo/js-keyboard/sounds/042.wav",
                69:"http://carolinegabriel.com/demo/js-keyboard/sounds/043.wav",
                68:"http://carolinegabriel.com/demo/js-keyboard/sounds/044.wav",
                70:"http://carolinegabriel.com/demo/js-keyboard/sounds/045.wav",
                84:"http://carolinegabriel.com/demo/js-keyboard/sounds/046.wav",
                71:"http://carolinegabriel.com/demo/js-keyboard/sounds/047.wav",
                89:"http://carolinegabriel.com/demo/js-keyboard/sounds/048.wav",
                72:"http://carolinegabriel.com/demo/js-keyboard/sounds/049.wav",
                85:"http://carolinegabriel.com/demo/js-keyboard/sounds/050.wav",
                74:"http://carolinegabriel.com/demo/js-keyboard/sounds/051.wav",
                75:"http://carolinegabriel.com/demo/js-keyboard/sounds/052.wav",
                79:"http://carolinegabriel.com/demo/js-keyboard/sounds/053.wav",
                76:"http://carolinegabriel.com/demo/js-keyboard/sounds/054.wav",
                80:"http://carolinegabriel.com/demo/js-keyboard/sounds/055.wav",
                186:"http://carolinegabriel.com/demo/js-keyboard/sounds/056.wav"};
           

const blackkeys = document.getElementsByClassName("blackkey"); /* list of the black keys on my page*/
const whitekeys = document.getElementsByClassName("whitekey"); // list of white keys on the page

const oldOne = document.getElementById("OldOne"); // OldOne image 

// For each key in the list of white keys, I am adding event listeners for hovering and not hovering 
for (const key of whitekeys)
{
  key.addEventListener("mouseover", ShowCharsOnWhiteHover);
  key.addEventListener("mouseleave", HideChars);

}

/**
 * This will make it so that when a white piano key is hovered it will display the text on every single key
 */
function ShowCharsOnWhiteHover(){
  for (const key of whitekeys)
  {
    key.style.color = "#000000";
  }
  for (const key of blackkeys)
  {
    key.style.color = "#ffffff";
  }
}

/* for each key in the list of black keys, add an event listener */
for (const key of blackkeys)
{
  key.addEventListener("mouseover", ShowCharsOnBlackHover);
  key.addEventListener("mouseleave", HideChars);
}

/**
 * This will make it so that when a black piano key is hovered it will display the text on every single key
 */
function ShowCharsOnBlackHover()
{
  for (const key of whitekeys)
  {
    key.style.color = "#000000";
  }
  for (const key of blackkeys)
  {
    key.style.color = "#ffffff";
  }
}

/**
 * this makes it so that when you hover off any of the piano keys, the text does not appear
 */
function HideChars()
{
  for (const key of whitekeys)
  {
    key.style.color = "";
  }
  for (const key of blackkeys)
  {
    key.style.color = "";
  }
}

/**
 * a function for handling when the great old one needs to be displayed
 */
function FoundSecret(){

    const scaryNoise = new Audio("https://orangefreesounds.com/wp-content/uploads/2020/09/Creepy-piano-sound-effect.mp3?_=1");
    scaryNoise.play();

    oldOne.style.zIndex = 100; //setting it to 100 just to make sure it sits on top of everything
    oldOne.style.transition = "opacity 2s";
    oldOne.style.opacity = 1;
    
};

//variables that are used for tracking whether or not the correct string is typed
//currentstring and secretnotfound need to be changed so they will not be const
//secretnotfound is a bool used to make it so that the piano keys can only be played when the great old one has not awoken
const secret = "weseeyou";
let currentString = ""; 
let secretnotfound = true;

//event listener for if a specific set of keys is pressed
document.addEventListener('keydown', function(PlayKey) {

  // I am holding a list of all the characters that can be typed to create a sound on my piano. I do not care about other
  // characters so I do not track the,
  const validWhiteKeys = ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';'];
  const validBlackKeys =  ['w', 'e', 't', 'y', 'u', 'o', 'p'];
  
  //if the key that is pressed is in the valid keys list
  if (validWhiteKeys.includes(PlayKey.key)) {
    for (const [index, element] of validWhiteKeys.entries()){ //enumerating through the validwhitekeys list
      if (PlayKey.key === element && secretnotfound) //done so that I can make sure that hitting a certain 
                                                      //key will correspond with triggering the correct piano key
      {
        whitekeys[index].style.background = "#b7b7bd"; //change the background color a little bit to indicate the key being hit
        setTimeout(() => {whitekeys[index].style.background = ""}, 100) //making sure color is only changed for 100ms

        const note = new Audio(sound[PlayKey.which]); //play the audio corresponding with the sound list
        note.play();

        currentString += PlayKey.key; //add the key pressed to the current string being tracked
        break;
      }
    }
  };
  if (validBlackKeys.includes(PlayKey.key)) {
    for (const [index, element] of validBlackKeys.entries()){ //same logic as the white keys
      if (PlayKey.key === element && secretnotfound)
      {
        blackkeys[index].style.background = "#b7b7bd";
        setTimeout(() => {blackkeys[index].style.background = ""}, 100)

        const note = new Audio(sound[PlayKey.which]);
        note.play();

        currentString += PlayKey.key;
        break;
      }
    }
  }
  for (let i = 0; i < currentString.length; i++)
  {
    if (currentString[i] != secret[i]) //if a character is typed that is not in the secret string
    {
      currentString = ""; // reset the current string to empty and break
      break;
    }
  }
  if (currentString === secret) //if string matches, call FoundSecret to display great old one
  {
    FoundSecret();
    currentString = "";
    secretnotfound = false; //set to false so that the keys cannot be played while the piano is not on screen
  }
});

