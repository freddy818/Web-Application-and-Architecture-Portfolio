let currWord = "";
let currLetter = 0;
let hidden_word ="";
let temp_hidden_word="";
let valid = false;
let gamedone = false;
let start_time = 0;
let leaderboardData = [];
let gamecompleted = false;

const instructions = document.getElementById('instructions');


const invalidWordNotif = "Word is invalid";

const invalidLettersNotif = "Not enough letters";

const leaderboard = document.getElementById('leaderboard');

const errornotif = document.getElementById('errornotif');

//An async function to create the board
async function CreateBoard() {
    const board = document.getElementById("board");
    await fetch('/get_hidden_word')
    .then(response => response.json())
    .then(data => {
        hidden_word = data.hidden_word;

        word_length = hidden_word.length;
        temp_hidden_word = hidden_word;
        temp_hidden_word = temp_hidden_word.toLowerCase();
        start_time = new Date(); 
        // fetch this data, store it into the variables, then start the timer by recording the date 
    });
    await fetch('/checkgamecompleted')
    .then(response => response.json())
    .then(data => {
        gamecompleted = data.game_completed;
        // I want to make sure a user cannot play multiple times a day, so it fetches a variable whether or not a user has played yet

    });

    if (gamecompleted > 0)
    {
        // if the user has  played today, then we want to show the leaderboard, set the gamedone to be tru
        gamedone = true;
        already_played = document.createElement('div');
        already_played.className = "leaderboardrow";
        already_played.textContent = `You already played today!`;
        leaderboard.appendChild(already_played);
        getLeaderboarData();
        GameDone();
    }

}

CreateBoard();

// something that will help me track whether or not I want to disable the game board
const disable = document.getElementById('disable'); 
keyboardbuttons = document.getElementsByClassName('keyboardbuttons');
letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'];

document.addEventListener('keydown', async function(key) {
   
    
    if (disable.textContent === 'True')
    {
        return;
    }
    // dont allow people to just hold a key and have it fill the row
    if (key.repeat)
    {
        return;
    }

    // if the game is done dont let the event listener do anything
    if (gamedone)
    {
         
        return;
    }

    // if they type add the key to the row
    //I am keeping track of what tile to add to by checking what letter they are currently on
    if (letters.includes(key.key.toLowerCase()))
    {
        tile = this.getElementsByClassName('boardtile')[currLetter];
        if (currWord.length < word_length)
        {
            tile.textContent = key.key;
            currWord += key.key;

            currLetter +=1;

        }
      
    }

    else if (key.key === 'Enter')
    {
        key.preventDefault(); //this got rid of a small bug that made it so when you clicked on the keyboard then pressed enter, it would sometimes type the letter twice
        tile = this.getElementsByClassName('boardtile');

        if (currWord.length < word_length)
        {
            //Pop an error notification when they try entering with too letters
            errornotif.textContent = invalidLettersNotif;
            errornotif.style.display = 'flex';
            setTimeout(function(){ errornotif.style.display = 'none'; }, 2000);
            return ///we don't want to do anything if someone tries entering before they have the right word length
            
        }

    
        else if ( currWord.length === word_length)
        {
            currWord = currWord.toLowerCase();
            hidden_word = hidden_word.toLowerCase();

            ///spell check if its a valid word here

            await checkValidWord(currWord);
            if (!valid)
            {
                //using an api to spell check, pop error notification if what was enterred is not a word
                errornotif.textContent = invalidWordNotif;
                errornotif.style.display = 'flex';
                setTimeout(function(){ errornotif.style.display = 'none'; }, 2000);

                return;
            }
 
            
            
            for (let i = 0; i < word_length; i++)
            {

                //if the current letter in the word is the exact same as the letter in the same position of the hidden word
                //I want to check the letters that are exactly correct first
                if (currWord[i] === hidden_word[i])
                {
                    //we want to make the tile green and then make that key on the keyboard green
                    tile[currLetter - word_length + i].style.background = "#00FF00";
                    temp_hidden_word = temp_hidden_word.replace(currWord[i], '');
                    tile[currLetter - word_length + i].style.color = "#FFFFFF";

                    colorKeyBoard(currWord[i], "#00FF00");

                }

            }


            for (let i = 0; i < word_length; i++)
            {
                //if the letter is in the word but not in the exact position, make it yellow
                //I am using a temp copy of the hidden word to check for this, if the letter is in the temp copy, i delete from the copy
                 //then i just recreate the copy at the end. This is done to handle cases where someone entered
                 // words with a repeat letter, it will make only the first letter turn yellow 
                if (temp_hidden_word.includes(currWord[i]) && currWord[i] !== hidden_word[i])
                {

                    tile[currLetter - word_length + i].style.background = "#8B8000";
                    temp_hidden_word = temp_hidden_word.replace(currWord[i], '');
                    tile[currLetter - word_length + i].style.color = "#FFFFFF";

                    colorKeyBoard(currWord[i], "#8B8000");

                }

                //turn letters gray if it is not in the word at all
                else if (currWord[i] !== hidden_word[i] && !temp_hidden_word.includes(currWord[i]))
                {
                    tile[currLetter - word_length + i].style.background = "#333333";
                    tile[currLetter - word_length + i].style.color = "#FFFFFF";
                    colorKeyBoard(currWord[i], "#333333");


                }
            }
            
            //apply a flip animation for the specific row when they submit a valid attempt
            applyFlip(tile, currLetter-word_length, currLetter-1);

            //reset the temporrary copy of the word
            temp_hidden_word = hidden_word;


            if (currWord === hidden_word || currLetter === word_length * word_length)
            {
                //set the game being done to true if they used last attempt or are correct
                gamedone = true;

                //Then we track their time by subtracting the current date by the date i set at the start
                var elapsed = (new Date() - start_time)/1000;
                
                //only add to the leaderboard if they correctly guessed the word
                if (currWord === hidden_word)
                {
                    await sendTime(elapsed);
                }

                ///get and create the leaderboard data
                getLeaderboarData();
                
                ///mark that the user has played the game today and should not be allowed to play again
                markCompleted();

                //Game is done
                setTimeout(GameDone, 2500);
            }
            //reset their current attempt
            currWord = "";
        }
    }

    ///handle deleting letters
    else if (key.key === 'Backspace')
    {
        tile = this.getElementsByClassName('boardtile')[currLetter-1];

        if (currWord.length > 0)
        { 
            tile.textContent = "";
            currLetter -= 1;
            currWord = currWord.substring(0, currWord.length-1);
        }
    }
});

// a function for coloring the keyboard after a valid guess
function colorKeyBoard(letterkey, hexcode)
{
    //Iterate through each of the keybuttons
    for (const keybutton of document.getElementsByClassName("keyboardbutton")) 
        {
    
        //if the key i am passing in is the same as the key that the loop is on
        if (keybutton.textContent.toLowerCase() === letterkey)
        {
            //If a key is already green, we do not want to change the color, so return
            if (keybutton.style.background === 'rgb(0, 255, 0)')
            {
                return;
            }
            //If a key is already yellow, and the color we are attempting to change it to is not green, do nothing
            else if (keybutton.style.background === 'rgb(139, 128, 0)' && hexcode !== 'rgb(0, 255, 0)')
            {
                return;
            }

            //Set the keybutton's background to the hexcode color
            keybutton.style.background = hexcode;
            break;
        }
    }
}

keyboard = document.getElementById('keyboard');
keyboard.addEventListener('click', (btn) =>
{
    ///Add an event listener that makes it so that it treats pressing the virtual keyboard the same as pressing
    //down on a key on your actual keyboard
    let key = btn.target.textContent;
    if (key === 'Delete')
        {
            key = 'Backspace'
        }
    document.dispatchEvent(new KeyboardEvent("keydown", {'key': key}))
})


//apply the flip animation
function applyFlip(tiles, starttile, endtile) {
    var tilesArray = Array.from(tiles);
    //for each tile in this range, flip it
    tilesArray.slice(starttile, endtile + 1).map(function (tile, i) {
        tile.classList.add("flip");
        tile.style.animationDelay = `${i * 100}ms`;
    });
}

//spell checking user attempts, fetch an api spellchecker
async function checkValidWord(currWord) {
    const url = `https://wordsapiv1.p.rapidapi.com/words/${currWord}`;
    const options = {
        method: 'GET',
        headers: {
            'X-RapidAPI-Key': 'ecd2152f85msha845931e39876b5p188823jsnd67ace51e7dd',
            'X-RapidAPI-Host': 'wordsapiv1.p.rapidapi.com'
        }
    };
    
    try {
        const response = await fetch(url, options)
        .then(response => response.json())
        .then(word => {
            if (word.word)
            {
                valid = true;
            }
            else
            {
                valid = false;

            }
    
        });
    } catch (error) {
        console.log('ERROR');
        valid = false;
    }

}

const closeinstructions = document.getElementById('closeinstructions')

const overlay = document.getElementById('overlay');
closeinstructions.addEventListener('click', closeInstructions);

//close the instructions, use this styling so not everything is just instant
function closeInstructions()
{
    disable.textContent = "False";
    instructions.style.display = 'none';
    overlay.style.transition = "opacity 2s";
    overlay.style.opacity = 0;
    setTimeout(function() {overlay.style.display = "none";}, 2000);

}

//stuff to do when the game is done
function GameDone()
{
    board.style.transition = "opacity 2s";
    board.style.opacity = 0;  
    leaderboard.style.transition = "opacity 4s";
    leaderboard.style.opacity = 100;

}

//fetch the leader board data, and then add to the html element that has the leaderboard id
async function getLeaderboarData()
{
    await fetch('/getleaderboarddata')
    .then(response => response.json())
    .then(data => {
        leaderboardData = data;

    });

    //create a row that will show the hidden word to the user
    reveal_word = document.createElement('div');
    reveal_word.className = "leaderboardrow";
    reveal_word.textContent = `The correct word is: ${hidden_word}`
    leaderboard.appendChild(reveal_word);

    //create a row that shows the title to the user
    title = document.createElement('div');
    title.className = 'leaderboardrow';
    title.textContent = 'The top 5 users of the day:';
    leaderboard.appendChild(title);

    //create a row in the leaderboard for each entry in the data fetched
    for (let q = 0; q < leaderboardData.length; q++)
                {
                    let rank = document.createElement('div');
                    rank.className = "leaderboardrow";
                    rank.textContent = `${q + 1}. ${leaderboardData[q][0]}: ${leaderboardData[q][1]}`;


                    leaderboard.appendChild(rank);

                }
}


//send to the leaderboard the users time to complete the game
async function sendTime(elapsed)
{
    await fetch('/getwordletime', 
    {
        headers: {
            'Content-Type': 'application/json'
          },
          method: 'POST',
          body: elapsed
    });
}

//mark that the user has now played the game in the database
async function markCompleted()
{
    await fetch('/markgamecompleted', 
    {
        headers: {
            'Content-Type': 'application/json'
          },
          method: 'POST',
    });
}