// notyf
const notyf = new Notyf({
  duration: 3000,
  position: {
    x: "right",
    y: "top",
  },
  ripple: true,
  dismissible: true,
});

// SIGN UP NOTYF
document.getElementById("signup_form").addEventListener("submit", async (e) => {
  e.preventDefault();

  const formData = new FormData(e.target);
  const response = await postForm("/register", formData);

  if (result.status === "ok") {
    notyf.success(result.message || "Registration successful!");
    setTimeout(() => {
      if (result.redirect_url) {
        window.location.href = result.redirect_url;
      } else {
        window.location.href = "/dashboard";
      }
    }, 3000);
  } else {
    notyf.error(result.message || "Registration failed!");
  }
});

// ADD TV NOTYF
function addTvToDOM(tvObject) {
  // <-- Receives tvObject
  const listContainer = document.getElementById("tv-card-grid");

  // 1. CRITICAL: Check if the container exists before trying to append!
  if (!listContainer) {
    console.error("Target container 'tv-card-grid' not found in the DOM.");
    notyf.error("Layout error: Cannot find TV grid.");
    return;
  }

  const newTvElement = document.createElement("div");

  newTvElement.className =
    "glass-card border-white/20 overflow-hidden hover:border-white/30 transition-all duration-300 group cursor-pointer rounded-lg shadow-lg relative tv-card"; // <-- Added 'tv-card' class
  newTvElement.id = `tv-card-${tvObject.tv_label.replace(/\s/g, "-")}`; // Added dynamic ID

  newTvElement.innerHTML = `
            <div class="relative h-40 overflow-hidden">
        <img
          src="{{ url_for('static', filename='images/tvs/tv3.jpeg') }}"
          alt="${tvObject.tv_label}"
          class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
        />
        <div
          class="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent"
        ></div>
        <div
          class="absolute inset-0 bg-gradient-to-br from-purple-500/20 to-blue-500/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
        ></div>

        <!-- Delete button (Placeholder form action) -->
        <div class="absolute top-3 right-3">
          <form method="POST" action="/delete-tv/${
            tvObject.tv_label
          }" onsubmit="return confirm('Delete this TV?');">
            <button
              type="submit"
              class="glass-card bg-red-500/20 hover:bg-red-500/40 text-red-300 hover:text-red-200 h-8 w-8 p-0 border border-red-400/30 rounded"
            >
              DELETE
            </button>
          </form>
        </div>
      </div>

      <!-- Card Header -->
      <div class="px-4 pt-4 flex align-center justify-between">
        <h3 class="text-lg text-white flex items-center space-x-2">
          <span>${
            tvObject.tv_label
          }</span> <!-- FIX: Changed tv.tv_label to tvObject.tv_label -->
          <span class="opacity-50 animate-spin">
            <svg
              class="h-4 w-4 text-blue-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 4v5h.582a7.5 7.5 0 0114.836 0H20V4h-5v.582a7.5 7.5 0 01-10.418 0H4z"
              />
            </svg>
          </span>
        </h3>

        <!-- ... Menu Dropdown (removed for brevity, no changes needed) ... -->

      </div>

      <!-- Card Content -->
      <div class="px-4 pb-4 space-y-4 text-sm text-gray-300 mt-4">
        <div class="flex items-center justify-between">
          <span>IP Address</span>
          <!-- FIX: Changed tv.tv_label to tvObject.ip_address (assuming your Flask backend returns this field) -->
          <span class="font-medium text-white">${
            tvObject.ip_address || "N/A"
          }</span>
        </div>

        <!-- Controls (using tvObject properties for dynamic actions) -->
        <form method="POST" action="/power-toggle/${tvObject.ip_address}">
          <button
            type="submit"
            class="w-full bg-[#da0000] text-white py-2 rounded power-button"
          >
            Power Toggle
          </button>
        </form>

        <!-- ... other controls using dynamic routes ... -->
        
        <div class="flex justify-between space-x-2">
          <form method="POST" action="volume-down/${tvObject.ip_address}">
            <button
              type="submit"
              class="bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded"
            >
              Vol -
            </button>
          </form>

          <form method="POST" action="volume-up/${tvObject.ip_address}">
            <button
              type="submit"
              class="bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded"
            >
              Vol +
            </button>
          </form>
        </div>
        
        <!-- ... Channel Controls ... -->

        <!-- connect button  -->
        <form action="/connect-samsung-tv/${tvObject.ip_address}" method="POST">
          <button
            type="submit"
            class="flex items-center space-x-2 text-gray-400 hover:text-white underline font-medium transition-transform duration-200 ease-in-out hover:-translate-y-1"
          >
            <!-- Minimal Connect Icon -->
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="20"
              height="20"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                d="M3 6a1 1 0 0 1 1-1h16a1 1 0 1 1 0 2H4a1 1 0 0 1-1-1Zm0 6a1 1 0 0 1 1-1h10a1 1 0 1 1 0 2H4a1 1 0 0 1-1-1Zm1 5a1 1 0 1 0 0 2h6a1 1 0 1 0 0-2H4Z"
              />
            </svg>
            <span>Connect to TV</span>
          </button>
        </form>
      </div>
    </div>
        `;
  listContainer.appendChild(newTvElement);
}

document.getElementById("add_tv_form").addEventListener("submit", async (e) => {
  e.preventDefault();

  const formData = new FormData(e.target);

  try {
    const response = await fetch("/add_tv", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      // Try to read server-side error message if available
      const errorText = await response.text();
      notyf.error(`Failed to add TV: ${errorText.substring(0, 80)}...`);
      throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
    }

    const result = await response.json();

    if (result.status === "ok" && result.tv_data) {
      notyf.success(`TV '${result.tv_data.tv_label}' added successfully!`);
      addTvToDOM(result.tv_data);
      e.target.reset();
      window.location.href = "/dashboard";
    } else {
      notyf.error("Failed to add TV: Server returned invalid data structure.");
    }
  } catch (err) {
    console.error("AJAX or Server Error: ", err);
    notyf.error("An unexpected server or network error occurred.");
  }
});
