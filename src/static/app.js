document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Clear activity dropdown before repopulating
      while (activitySelect.options.length > 1) {
        activitySelect.remove(1);
      }

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        // Generate participants list
        let participantsList = '';
        if (details.participants && details.participants.length > 0) {
          participantsList = details.participants
            .map(participant => `
              <li>
                <span class="participant-email">${participant}</span>
                <button type="button" class="participant-remove" data-activity="${name}" data-email="${participant}" aria-label="Remove ${participant}">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                    <path d="M3 6h18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    <path d="M8 6V4h8v2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    <path d="M10 11v6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    <path d="M14 11v6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    <path d="M6 6l1 14h10l1-14" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                  </svg>
                </button>
              </li>
            `)
            .join('');
        } else {
          participantsList = '<li style="color: #999; font-style: italic;">No participants yet</li>';
        }

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-section">
            <h5>Current Participants:</h5>
            <ul class="participants-list">
              ${participantsList}
            </ul>
          </div>
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  async function removeParticipant(activityName, email) {
    const response = await fetch(
      `/activities/${encodeURIComponent(activityName)}/participants?email=${encodeURIComponent(email)}`,
      {
        method: "DELETE",
      }
    );

    if (!response.ok) {
      const result = await response.json();
      throw new Error(result.detail || "Failed to remove participant");
    }

    return response.json();
  }

  activitiesList.addEventListener("click", async (event) => {
    const button = event.target.closest(".participant-remove");
    if (!button) return;

    const activityName = button.dataset.activity;
    const email = button.dataset.email;

    button.disabled = true;
    try {
      await removeParticipant(activityName, email);
      await fetchActivities();
    } catch (error) {
      console.error("Error removing participant:", error);
      button.disabled = false;
    }
  });

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        // Refresh activities list immediately to show new participant
        setTimeout(() => {
          fetchActivities();
        }, 500);
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
