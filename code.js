let dealerSum = 0;
let yourSumA = 0;
let yourSumB = 0;
let decks = 6;
let count = 0;

let temp = "";

let dealerAceCount = 0;
let yourAceCountA = 0; 
let yourAceCountB = 0; 

let dealerCards = [];
let yourCardsA = [];
let yourCardsB = [];
let hits = 0;;
let outcome = 0;

let hidden;
let deck;

let balance = 1000;
let bet = 50;
let betA = 0;
let betB = 0;

let message = " ";

let canHit = false;
let canDeal = true;
let canStay = true;
let canSplit = false;
let isSplit = false;
let onSecond = false;
let action = "";


//startGame();
window.onload = function() {
    buildDeck();
    shuffleDeck(); 
    getScore();
    SaveScore();
    document.getElementById("balance").textContent = "Balance: $" + balance; 
    document.getElementById("results").textContent = message;
}

function sleep(ms = 0){
    return new Promise(resolve => setTimeout(resolve, ms));
}

function logGameData() {
    const gameData = {
        dealerSum: dealerSum,
        yourSumA: yourSumA,
        yourSumB: yourSumB,
        dealerCards: dealerCards,
        yourCardsA: yourCardsA,
        yourCardsB: yourCardsB,
        balance: balance,
        bet: bet,
        action: action,
        outcome: outcome,
    };
    sendGameDataToServer(gameData);
}

function sendGameDataToServer(gameData) {
    fetch('/saveGameData', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(gameData)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

async function play100Games() {
    for (let i = 0; i < 10; i++) {
        startGame(); // Start a new game
        let randomAction = -1; // Initialize to a value other than 3

        // Randomly decide on actions until the game is over
        while (randomAction !== 3) {
            randomAction = Math.floor(Math.random() * 5); // Generate a random number from 0 to 4
            switch (randomAction) {
                case 0:
                    hit();
                    sleep(10);
                    break;
                case 1:
                    split();
                    sleep(10);
                    break;
                case 2:
                    double();
                    sleep(10);
                    break;
                case 3:
                    stay();
                    break;
                default:
                    break;
            }
        }
    }
}



const switchInput = document.getElementById('switch');
const displayNumber = document.getElementById('displayNumber');

switchInput.addEventListener('change', function() {
    if (this.checked) {
        displayNumber.textContent = 'Count: ' + count; // Change the number here
    } else {
        displayNumber.textContent = ''; // Reset the number when the switch is off
    }
});

function updateDisplayNumber() {
    if (switchInput.checked) {
        displayNumber.textContent = 'Count: ' + count;
    }
}

$(document).ready(function() {
    $('.minus').click(function () {
        var $input = $(this).parent().find('input');
        var count = parseInt($input.val()) - 25;
        count = count < 25 ? 25 : count;
        $input.val(count);
        $input.change();
        bet = count;
        console.log("count " + count);
        console.log("bet " + bet);
        return false;
    });
    $('.plus').click(function () {
        var $input = $(this).parent().find('input');
        $input.val(parseInt($input.val()) + 25);
        $input.change();
        bet = $input.val();
        console.log("count " + $input.val());
        console.log("bet " + bet);
        return false;
    });
});

function SaveScore() {
    const formData = new FormData();
    formData.set('score', balance);
    fetch('/setScore', {
        method: 'POST',
        body: formData,
        credentials: 'same-origin'
    })
    .then(response => {
        if (response.ok) {
            console.log('Score saved successfully');
        } else {
            console.error('Failed to save score');
        }
    })
    .catch(error => {
        console.error('Error saving score:', error);
    });
}

function getScore() {
    fetch('/getScore', {
        method: 'GET',
        credentials: 'same-origin'
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Failed to fetch score');
        } 
    })
    .then(data => {
        console.log('Received score data:', data); // Check the received data
        const score = data.score;
        console.log('Parsed score:', score); // Check the parsed score
        balance = score;
        console.log('Updated balance:', balance); // Check if balance is updated

        // Update the balance on the page
        document.getElementById("balance").textContent = "Balance: $" + balance;
    })
    .catch(error => {
        console.error('Error fetching score:', error);
    });
}



function buildDeck() {
    let values = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"];
    let types = ["Clubs", "Diamonds", "Hearts", "Spades"];
    deck = [];

    for (let a = 0; a < decks; a++){
        for (let i = 0; i < types.length; i++) {
            for (let j = 0; j < values.length; j++) {
                deck.push(values[j] + types[i]); 
            }
        }
    }
    // console.log(deck);
}

async function shuffleDeck() {
    const shuffle2 = document.getElementById("shuffle1");
    const shuffle3 = document.getElementById("shuffle2");
    console.log(shuffle2); 
    message = "shuffling";
    document.getElementById("results").textContent = message;

    for (let i = 0; i < deck.length; i++) {
        let j = Math.floor(Math.random() * deck.length);
        let temp = deck[i];
        deck[i] = deck[j];
        deck[j] = temp;
    }
    
    shuffle2.classList.add("shuffleAnimation1");
    await sleep(500);
    shuffle3.classList.add("shuffleAnimation2");
    console.log("Animation started"); 
    await sleep(2000);
    shuffle2.classList.remove('shuffleAnimation1');
    shuffle3.classList.remove('shuffleAnimation2');
    console.log("Animation ended"); 
    console.log(deck);
    document.getElementById("results").textContent = "";
}

async function startGame() {
    if (!canDeal || bet > balance) {
        return;
    }
    var elements = document.querySelectorAll('[id^="dealer-card"]');
    elements.forEach(function(el){
        el.parentNode.removeChild(el);
    });
    elements = document.querySelectorAll('[id^="player-card"]');
    elements.forEach(function(el){
        el.parentNode.removeChild(el);
    });
    if(deck.length < 52 * decks / 2){
        shuffleDeck();
        await sleep(2000);
    } 
    canHit = true;
    message = " ";
    canStay = true;
    isSplit = false;
    isDouble = false;
    canHit = true;
    canDeal = false;
    dealerSum = 0;
    yourSumA = 0;
    yourSumB = 0;
    hits = 0;
    dealerAceCount = 0;
    yourAceCountA = 0; 
    yourAceCountB = 0; 
    dealerCards = [];
    yourCardsA = [];
    yourCardsB = [];
    betA = bet;
    betB = bet;
    temp = "";
    hidden = deck.pop();
    dealerSum += getValueFirst(hidden);
    dealerAceCount += checkAce(hidden);
    let cardImg = document.createElement("img");
    cardImg.src = "../static/Back.png";
    cardImg.id = "dealer-card-" + hidden;
    cardImg.className = "cards";
    cardImg.classList.add("dealerAnimation" + (dealerCards.length + 1));
    document.getElementById("card-container").append(cardImg);
    cardImg = document.createElement("img");
    let card = deck.pop();
    cardImg.src = "../static/" + card + ".png";
    dealerSum += getValue(card);
    dealerAceCount += checkAce(card);
    cardImg.id = "dealer-card-" + card;
    cardImg.className = "cards";
    dealerCards.push( getValue(card) );
    cardImg.classList.add("dealerAnimation" + (dealerCards.length + 1));
    document.getElementById("card-container").append(cardImg);
    for (let i = 0; i < 2; i++) {
        let cardImg = document.createElement("img");
        let card = deck.pop();
        cardImg.src = "../static/" + card + ".png";
        yourSumA += getValue(card);
        yourAceCountA += checkAce(card);
        yourCardsA.push( getValue(card) );
        cardImg.id = "player-card-" + yourCardsA.length;
        cardImg.className = "cards";
        cardImg.classList.add("playerAnimation" + yourCardsA.length);
        document.getElementById("card-container").append(cardImg);
        if(temp != card[0]){
            temp = card[0];
        } else if (temp == card[0]){
            canSplit = true;
        }
    }
    if(yourSumA == 21){
        //betA = bet * 1.5;
        stay();
    }
}

function split() {
    if (!canSplit || bet * 2 > balance) {
        return;
    }
    canSplit = false;
    isSplit = true;
    yourSumA = getValueFirst(temp);
    yourSumB = getValueFirst(temp);
    yourAceCountA = checkAce(temp);
    yourAceCountB = checkAce(temp);
    yourCardsB.push(yourCardsA.pop());
    let player = document.getElementById('player-card-1');
    if (player) { 
        player.classList.remove('playerAnimation1');
        player.classList.add('moveLeft');
    } else {
        console.log("Element 'player-card-1' not found");
    }

    player = document.getElementById('player-card-2');
    if (player) {
        player.classList.remove('playerAnimation2');
        player.classList.add('moveRight');
    } else {
        console.log("Element 'player-card-2' not found");
    }
    action = "split"
    logGameData();
}

function double(){
    if (!canHit || bet * 2 > balance) {
        return;
    }
    if(!onSecond && yourCardsA.length != 2){
        return;
    }
    if(onSecond && yourCardsB.length != 2){
        return;
    }
    let cardImg = document.createElement("img");
    let card = deck.pop();
    cardImg.src = "../static/" + card + ".png";
    cardImg.className = "cards";
    if(!onSecond){
        yourSumA += getValue(card);
        yourAceCountA += checkAce(card);
        cardImg.id = "player-card-A-" + card;
        yourCardsA.push(getValue(card));
        if(!isSplit){
            cardImg.classList.add("playerAnimation" + yourCardsA.length);
        } else {
            cardImg.classList.add("playerAnimationA" + yourCardsA.length);
        }
        document.getElementById("card-container").append(cardImg);
        canHit = false;
        betA = bet * 2;
        action = "doubleA"
        logGameData();
    } else {
        yourSumB += getValue(card);
        yourAceCountB += checkAce(card);
        cardImg.id = "player-card-B-" + card;
        yourCardsB.push(getValue(card));
        cardImg.classList.add("playerAnimationB" + yourCardsB.length);
        document.getElementById("card-container").append(cardImg);
        canHit = false;
        betB = bet * 2;
        action = "doubleB"
        logGameData();
    }
    stay();
}


function hit() {
    if (!canHit) {
        return;
    }
    hits++;
    canSplit = false;
    let cardImg = document.createElement("img");
    let card = deck.pop();
    cardImg.src = "../static/" + card + ".png";
    cardImg.className = "cards";
    if(!onSecond){
        yourSumA += getValue(card);
        yourAceCountA += checkAce(card);
        cardImg.id = "player-card-A-" + card;
        yourCardsA.push(getValue(card));
        if(!isSplit){
            cardImg.classList.add("playerAnimation" + yourCardsA.length);
        } else {
            cardImg.classList.add("playerAnimationA" + yourCardsA.length);
        }
        document.getElementById("card-container").append(cardImg);
        action = "hitA"
        logGameData();
        if (reduceAce(yourSumA, yourAceCountA) >= 21) { 
            canHit = false;
            stay();
        }
    } else {
        yourSumB += getValue(card);
        yourAceCountB += checkAce(card);
        cardImg.id = "player-card-B-" + card;
        yourCardsB.push(getValue(card));
        cardImg.classList.add("playerAnimationB" + yourCardsB.length);
        document.getElementById("card-container").append(cardImg);
        action = "hitB"
        logGameData();
        if (reduceAce(yourSumB, yourAceCountB) >= 21) { 
            canHit = false;
            stay();
        }
    }
}

async function stay() {
    if (!canStay) {
        return;
    }
    if (isSplit && !onSecond){
        onSecond = true;
        canHit = true;
        return;
    }
    canHit = false;
    canStay = false;
    getValue(hidden);
    document.getElementById("dealer-card-" + hidden).src = "../static/" + hidden + ".png";
    dealerCards.push(getValue(hidden));
    while (dealerSum < 17 || (dealerSum == 17 && dealerAceCount > 0)) {
        dealerSum = reduceAce(dealerSum, dealerAceCount);
        await sleep(1000);
        let cardImg = document.createElement("img");
        let card = deck.pop();
        cardImg.src = "../static/" + card + ".png";
        dealerSum += getValue(card);
        dealerAceCount += checkAce(card);
        cardImg.id = "dealer-card-" + card;
        cardImg.className = "cards";
        dealerCards.push(getValue(card));
        cardImg.classList.add("dealerAnimation" + dealerCards.length);
        document.getElementById("card-container").append(cardImg);
        document.getElementById("results").textContent = message;
    }
    dealerSum = reduceAce(dealerSum, dealerAceCount);
    console.log("dealerSum: " + dealerSum);
    
    yourSumA = reduceAce(yourSumA, yourAceCountA);
    console.log("yourSumA: " + yourSumA);

    action = "stay"
    logGameData();
    if(yourSumA == 21 && yourCardsA.length == 2){
        message = "21!";
        balance += parseFloat(betA * 1.5);
    }
    else if (yourSumA > 21) {
        message = "You Lose!";
        balance -= parseFloat(betA);
    }
    else if (dealerSum > 21) {
        message = "You Win!";
        balance += parseFloat(betA);
    }
    else if (yourSumA == dealerSum) {
        message = "Tie!";
    }
    else if (yourSumA > dealerSum) {
        message = "You Win!";
        balance += parseFloat(betA);
    }
    else if (yourSumA < dealerSum) {
        message = "You Lose!";
        balance -= parseFloat(betA);
    }
    if(isSplit){
        yourSumB = reduceAce(yourSumB, yourAceCountB);
        console.log("yourSumB: " + yourSumB);
        if(yourSumB == 21 && yourCardsB.length == 2){
            message = "21!";
            balance += parseFloat(betB * 1.5);
        }
        else if (yourSumB > 21) {
            message += " You Lose!";
            balance -= parseFloat(betB);
        }
        else if (dealerSum > 21) {
            message += " You Win!";
            balance += parseFloat(betB);
        }
        else if (yourSumB == dealerSum) {
            message += " Tie!";
        }
        else if (yourSumB > dealerSum) {
            message += " You Win!";
            balance += parseFloat(betB);
        }
        else if (yourSumB < dealerSum) {
            message += " You Lose!";
            balance -= parseFloat(betB);
        }
    }

    canDeal = true;
    document.getElementById("results").textContent = message;
    document.getElementById("balance").textContent = "Balance: $" + balance;
 
    console.log("balance: " + balance);
    SaveScore();
}

function getValue(card) {
    if(card[0] == 'A'){
        count -= 1;
        updateDisplayNumber();
        return 11;
    }
    if(card[0] == 'J' || card[0] == 'Q' || card[0] == 'K'){
        count -= 1;
        updateDisplayNumber();
        return 10;
    }
    if(card[0] == '1'){
        count -= 1;
        updateDisplayNumber();
        return 10;
    }
    if(parseInt(card[0]) >= 2 && parseInt(card[0]) <= 6){
        count += 1;
    }
    updateDisplayNumber();
    return parseInt(card[0]);
}

function getValueFirst(card) {
    if(card[0] == 'A'){
        return 11;
    }
    if(card[0] == 'J' || card[0] == 'Q' || card[0] == 'K'){
        return 10;
    }
    if(card[0] == '1'){
        return 10;
    }
    return parseInt(card[0]);
}

function checkAce(card) {
    if (card[0] == "A") {
        return 1;
    }
    return 0;
}

function reduceAce(playerSum, playerAceCount) {
    while (playerSum > 21 && playerAceCount > 0) {
        playerSum -= 10;
        playerAceCount -= 1;
    }
    return playerSum;
}

