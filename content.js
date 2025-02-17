let popup = null;

// Listen for keydown events
document.addEventListener('keydown', async (e) => {
  // Check if 'e' key is pressed and text is selected
  if (e.key.toLowerCase() === 'e') {
    const selectedText = window.getSelection().toString().trim();
    
    if (selectedText) {
      if (popup) {
        popup.remove();
      }

      try {
        // Get the API key from storage
        const result = await chrome.storage.local.get(['groqApiKey']);
        if (!result.groqApiKey) {
          showPopup(selectedText, "Please set your Groq API key in the extension popup. Click the extension icon in your toolbar to add your key.");
          return;
        }

        showPopup(selectedText, "Loading explanation...");

        const response = await fetch('https://api.groq.com/v1/chat/completions', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${result.groqApiKey}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            model: "mixtral-8x7b-32768",
            messages: [
              {
                role: "user",
                content: `Please explain the meaning and context of: ${selectedText}`
              }
            ],
            temperature: 0.7
          })
        });

        if (response.ok) {
          const data = await response.json();
          showPopup(selectedText, data.choices[0].message.content);
        } else {
          showPopup(selectedText, "Error: Failed to get response from Groq. Please check your API key.");
        }
      } catch (error) {
        console.error('Error:', error);
        showPopup(selectedText, "Error connecting to Groq API. Please check your API key and internet connection.");
      }
    }
  }
});

function showPopup(selectedText, explanation) {
  popup = document.createElement('div');
  popup.style.cssText = `
    position: absolute;
    top: ${window.getSelection().getRangeAt(0).getBoundingClientRect().bottom + window.scrollY + 10}px;
    left: ${window.getSelection().getRangeAt(0).getBoundingClientRect().left + window.scrollX}px;
    background: white;
    border: 1px solid #ccc;
    border-radius: 4px;
    padding: 10px;
    max-width: 300px;
    max-height: 200px;
    overflow-y: auto;
    z-index: 10000;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    font-family: Arial, sans-serif;
  `;
  
  popup.innerHTML = `
    <div style="font-weight: bold;">Selected text:</div>
    <div style="margin-bottom: 10px;">${selectedText}</div>
    <div style="font-weight: bold;">Explanation:</div>
    <div>${explanation}</div>
  `;

  document.body.appendChild(popup);

  // Close popup when clicking outside
  document.addEventListener('mousedown', (e) => {
    if (popup && !popup.contains(e.target)) {
      popup.remove();
    }
  });
} 