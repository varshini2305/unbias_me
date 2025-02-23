// Listen for messages from the popup
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.action === "getBlogText") {
      let blogText = "";
      // Try to extract text from an <article> element if available
      let article = document.querySelector("article");
      if (article) {
        blogText = article.innerText;
      } else {
        // If no <article>, fall back to concatenating all paragraphs
        let paragraphs = document.querySelectorAll("p");
        blogText = Array.from(paragraphs).map(p => p.innerText).join("\n");
      }
      sendResponse({ blogText: blogText });
    }
  });
  