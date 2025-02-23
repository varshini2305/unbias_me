document.addEventListener("DOMContentLoaded", function() {
    const critiqueDisplay = document.getElementById("critiqueDisplay");
    const userInput = document.getElementById("userInput");
    const analyzeBtn = document.getElementById("analyzeBtn");
  
    // Query the active tab and ask the content script for blog text
    chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
      chrome.tabs.sendMessage(tabs[0].id, { action: "getBlogText" }, function(response) {
        if (response && response.blogText) {
          userInput.value = response.blogText;
          // Optionally, you can automatically analyze on load:
          sendAPIRequest(response.blogText);
        } else {
          critiqueDisplay.innerText = "No blog text found on this page.";
        }
      });
    });
  
    analyzeBtn.addEventListener("click", function() {
      const text = userInput.value;
      sendAPIRequest(text);
    });
  
    function sendAPIRequest(text) {
      const apiUrl = "https://1b0a-2001-468-300-800-d55d-2794-f78-5e65.ngrok-free.app/analyze";
      
      var myHeaders = new Headers();
      myHeaders.append("Content-Type", "application/json");
  
      var raw = JSON.stringify({ "paragraph": text });
  
      var requestOptions = {
        method: 'POST',
        headers: myHeaders,
        body: raw,
        redirect: 'follow'
      };
  
      fetch(apiUrl, requestOptions)
        .then(response => response.json())
        .then(result => {
          // Expecting result to have keys "text" and "critique"
          critiqueDisplay.innerText = result.critique || "No critique provided.";
        })
        .catch(error => {
          console.error('error', error);
          critiqueDisplay.innerText = "Error: " + error;
        });
    }
  });
  