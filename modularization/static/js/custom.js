document.addEventListener("click", function(e) {
    var item = e.target.closest(".session-item");
    var optionsBtn = e.target.closest(".options");
    var modal = document.getElementById('modal');
  
    // Handle session item click to load chat
    if (item && !optionsBtn) {
      console.log("[DEBUG] Clicked .session-item with index:", item.dataset.index);
  
      // We select the actual <textarea> inside #session-select-callback
      var hiddenBox = document.querySelector("#session-select-callback textarea");
      if (hiddenBox) {
        hiddenBox.value = item.dataset.index;
        console.log("[DEBUG] Setting hidden callback value:", hiddenBox.value);
        // Dispatch 'input' event to match .input(...) in Python
        hiddenBox.dispatchEvent(new Event("input", { bubbles: true }));
      } else {
        console.log("[DEBUG] #session-select-callback textarea not found!");
      }
    }
  
    // Handle options button click to toggle modal visibility
    if (optionsBtn) {
      console.log("[DEBUG] Options button clicked for session ID:", optionsBtn.dataset.sessionId);
      
      if (!modal) {
        console.error("[ERROR] Modal with id 'modal' not found!");
        return;
      }
  
      // Toggle visibility of the modal
      if (modal.style.display === "none" || modal.style.display === "") {
        console.log("[DEBUG] Showing modal");
        modal.style.display = "block";  // Show the modal
        var rect = optionsBtn.getBoundingClientRect();
        console.log("[DEBUG] Positioning modal at top:", rect.bottom + window.scrollY, "left:", rect.left);
        // Position the modal just below the options div
        modal.style.top = (rect.bottom + window.scrollY + 50) + "px";
        modal.style.left = (rect.left + 40) + "px";  // Align the modal with the options div
      }
    } 
    // Close the modal if it's open and clicked anywhere else
    else if (modal && modal.style.display === "block") {
      console.log("[DEBUG] Clicking outside of options button, closing modal.");
      modal.style.display = "none";  // Close the modal
    }
  
    // Handle rename button click
    if (e.target.classList.contains('rename-btn')) {
      var sessionId = optionsBtn ? optionsBtn.dataset.sessionId : null;
      console.log("[DEBUG] Rename button clicked for session ID:", sessionId);
      var newName = prompt("Enter new session name:");
      if (newName) {
        console.log("[DEBUG] Renaming session:", newName);
        // Implement the renaming logic here
        modal.style.display = "none"; // Close modal after renaming
      }
    }
  
    // Handle delete button click
    if (e.target.classList.contains('delete-btn')) {
      var sessionId = optionsBtn ? optionsBtn.dataset.sessionId : null;
      console.log("[DEBUG] Delete button clicked for session ID:", sessionId);
      if (confirm("Are you sure you want to delete this session?")) {
        console.log("[DEBUG] Deleting session with ID:", sessionId);
        // Implement the delete logic here
        modal.style.display = "none"; // Close modal after deleting
      }
    }
  });