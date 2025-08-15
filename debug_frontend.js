// ENHANCED Debug script to run in browser console
// Copy and paste this into the browser developer console (F12) when on the historical-robust page

console.log("=== ENHANCED Debug Script Starting ===");

// Check current date picker value
const datePicker = document.getElementById('analysis-date');
console.log("Date picker value:", datePicker ? datePicker.value : "DATE PICKER NOT FOUND");

// Check if games are in the DOM immediately
const gameCards = document.querySelectorAll('.game-card');
console.log("Current game cards found:", gameCards.length);

// Enhanced debugging function
function debugGameCards() {
    console.log("\n=== DETAILED GAME CARD ANALYSIS ===");
    
    const gameCards = document.querySelectorAll('.game-card');
    console.log("Total game cards:", gameCards.length);
    
    if (gameCards.length > 0) {
        // Analyze first 3 game cards
        for (let i = 0; i < Math.min(3, gameCards.length); i++) {
            const card = gameCards[i];
            console.log(`\n--- Game Card ${i + 1} ---`);
            
            // Check team names
            const awayTeam = card.querySelector('.away-team');
            const homeTeam = card.querySelector('.home-team');
            console.log("Teams:", awayTeam?.textContent, "vs", homeTeam?.textContent);
            
            // Check score elements
            const finalScore = card.querySelector('.final-score');
            const gameTime = card.querySelector('.game-time');
            const gameScore = card.querySelector('.game-score');
            
            console.log("Final score element:", finalScore ? finalScore.textContent : "NOT FOUND");
            console.log("Game time element:", gameTime ? gameTime.textContent : "NOT FOUND");
            console.log("Game score container:", gameScore ? gameScore.innerHTML : "NOT FOUND");
            
            // Check if score container is empty or hidden
            if (gameScore) {
                const computedStyle = window.getComputedStyle(gameScore);
                console.log("Game score visibility:", computedStyle.visibility);
                console.log("Game score display:", computedStyle.display);
                console.log("Game score innerHTML:", gameScore.innerHTML);
            }
        }
        
        // Summary counts
        const finalScores = document.querySelectorAll('.final-score');
        const gameTimes = document.querySelectorAll('.game-time');
        console.log(`\n=== SUMMARY ===`);
        console.log("Final score elements:", finalScores.length);
        console.log("Game time elements:", gameTimes.length);
        
        if (finalScores.length > 0) {
            console.log("Sample final scores:");
            for (let i = 0; i < Math.min(3, finalScores.length); i++) {
                console.log(`  ${i + 1}: "${finalScores[i].textContent}"`);
            }
        }
        
        if (gameTimes.length > 0) {
            console.log("Sample game times:");
            for (let i = 0; i < Math.min(3, gameTimes.length); i++) {
                console.log(`  ${i + 1}: "${gameTimes[i].textContent}"`);
            }
        }
    } else {
        console.log("No game cards found in DOM!");
    }
}

// Run immediately
debugGameCards();

// If currently on a different date, force load August 12th
if (datePicker && datePicker.value !== '2025-08-12') {
    console.log("\nSwitching to August 12th...");
    datePicker.value = '2025-08-12';
    
    if (typeof loadAnalysis === 'function') {
        loadAnalysis();
        
        // Debug again after loading
        setTimeout(() => {
            console.log("\n=== AFTER LOADING AUGUST 12TH ===");
            debugGameCards();
        }, 3000);
    }
}

console.log("=== ENHANCED Debug Script Complete ===");
