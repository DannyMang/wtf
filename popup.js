document.addEventListener('DOMContentLoaded', () => {
  const apiKeyInput = document.getElementById('apiKey');
  const saveButton = document.getElementById('saveKey');

  // Load saved API key
  chrome.storage.local.get(['groqApiKey'], (result) => {
    if (result.groqApiKey) {
      apiKeyInput.value = result.groqApiKey;
    }
  });

  // Save API key
  saveButton.addEventListener('click', () => {
    const apiKey = apiKeyInput.value;
    chrome.storage.local.set({ groqApiKey: apiKey }, () => {
      document.getElementById('explanation').textContent = 'API key saved!';
    });
  });
}); 