// Global variables
let downloadInfo = null;

// Show alert function
function showAlert(message, type = "danger") {
  const alertContainer = document.getElementById("alertContainer");
  const alertHTML = `
                <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                    <i class="fas fa-${
                      type === "success"
                        ? "check-circle"
                        : "exclamation-triangle"
                    } me-2"></i>
                    ${message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
  alertContainer.innerHTML = alertHTML;
}

// Format file size
function formatFileSize(bytes) {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
}

// Update progress
function updateProgress(step, percent, statusText) {
  const progressBar = document.getElementById("progressBar");
  const statusElement = document.getElementById("statusText");

  statusElement.textContent = statusText;
  progressBar.style.width = percent + "%";
  progressBar.textContent = percent + "%";
}

// Handle form submission
document.getElementById("scrapeForm").addEventListener("submit", function (e) {
  e.preventDefault();

  const form = this;
  const btn = document.getElementById("scrapeBtn");
  const progressSection = document.getElementById("progressSection");
  const fileInfoSection = document.getElementById("fileInfoSection");
  const filmUrl = document.getElementById("film_url").value.trim();

  if (!filmUrl) {
    showAlert("URL film tidak boleh kosong!");
    return;
  }

  // Reset UI
  document.getElementById("alertContainer").innerHTML = "";
  fileInfoSection.classList.add("d-none");

  // Disable button and show progress
  btn.disabled = true;
  btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Menganalisis...';
  progressSection.classList.remove("d-none");

  // Progress steps
  const steps = [
    { text: "Mengakses halaman film...", percent: 20 },
    { text: "Mencari link Buzzheavier...", percent: 40 },
    { text: "Mengakses Buzzheavier...", percent: 60 },
    { text: "Mencari link download...", percent: 80 },
    { text: "Mendapatkan informasi file...", percent: 90 },
    { text: "Analisis selesai!", percent: 100 },
  ];

  let currentStep = 0;

  // Simulate progress
  const progressInterval = setInterval(() => {
    if (currentStep < steps.length - 1) {
      updateProgress(
        currentStep,
        steps[currentStep].percent,
        steps[currentStep].text
      );
      currentStep++;
    } else {
      clearInterval(progressInterval);
    }
  }, 1500);

  // Make API call
  fetch("/api/get_download_info", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ film_url: filmUrl }),
  })
    .then((response) => response.json())
    .then((data) => {
      clearInterval(progressInterval);

      if (data.success) {
        // Show final step
        updateProgress(5, 100, "Analisis selesai!");

        // Store download info
        downloadInfo = data;

        // Show file info
        document.getElementById("filmTitle").textContent =
          data.film_title || "Unknown";
        document.getElementById("fileName").textContent = data.filename;

        // Format and display file size
        const fileSizeText =
          data.file_size > 0
            ? formatFileSize(data.file_size)
            : "Ukuran tidak diketahui";
        document.getElementById("fileSize").textContent = fileSizeText;

        // Add warning if file size is unknown
        if (data.file_size === 0) {
          document.getElementById("fileSize").innerHTML =
            '<span class="text-warning">Ukuran tidak diketahui</span> <i class="fas fa-exclamation-triangle text-warning" title="Server tidak memberikan informasi ukuran file"></i>';
        }

        document.getElementById("buzzLink").textContent = data.buzzheavier_link;

        fileInfoSection.classList.remove("d-none");

        showAlert("Analisis berhasil! File siap untuk didownload.", "success");
      } else {
        throw new Error(data.error || "Unknown error");
      }
    })
    .catch((error) => {
      clearInterval(progressInterval);
      updateProgress(0, 0, "Error: " + error.message);
      document.getElementById("progressBar").classList.add("bg-danger");
      showAlert("Error: " + error.message);
    })
    .finally(() => {
      btn.disabled = false;
      btn.innerHTML =
        '<i class="fas fa-search me-2"></i>Analisis & Siapkan Download';
    });
});

// Handle download button click
document.addEventListener("click", function (e) {
  if (e.target.id === "downloadBtn" && downloadInfo) {
    const downloadBtn = document.getElementById("downloadBtn");

    // Update button state
    downloadBtn.disabled = true;
    downloadBtn.innerHTML =
      '<i class="fas fa-spinner fa-spin me-2"></i>Memulai Download...';
    downloadBtn.classList.remove("pulse");

    // Create download URL
    const downloadUrl = `/download?filename=${encodeURIComponent(
      downloadInfo.filename
    )}&url=${encodeURIComponent(downloadInfo.flashbang_link)}`;

    // Create hidden link and trigger download
    const link = document.createElement("a");
    link.href = downloadUrl;
    link.download = downloadInfo.filename;
    link.style.display = "none";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    // Show success message
    showAlert(
      `Download dimulai! File "${downloadInfo.filename}" akan tersimpan di folder Downloads Anda.`,
      "success"
    );

    // Reset button after delay
    setTimeout(() => {
      downloadBtn.disabled = false;
      downloadBtn.innerHTML =
        '<i class="fas fa-download me-2"></i>Download Film Sekarang';
      downloadBtn.classList.add("pulse");
    }, 3000);
  }
});

document.addEventListener("DOMContentLoaded", function () {
  const scrapeForm = document.getElementById("scrapeForm");
  const progressSection = document.getElementById("progressSection");
  const filmInfoSection = document.getElementById("filmInfoSection");
  const progressBar = document.getElementById("progressBar");
  const statusText = document.getElementById("statusText");
  const alertContainer = document.getElementById("alertContainer");
  const downloadBtn = document.getElementById("downloadBtn");
  const downloadBtnText = document.getElementById("downloadBtnText");
  const scrapeBtn = document.getElementById("scrapeBtn");
  const scrapeBtnText = document.getElementById("scrapeBtnText");

  let downloadData = null;

  // Form submission handler
  scrapeForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    const filmUrl = document.getElementById("film_url").value.trim();
    if (!filmUrl) {
      showAlert("Masukkan URL film terlebih dahulu!", "warning");
      return;
    }

    // Disable form and show loading state
    scrapeBtn.disabled = true;
    scrapeBtnText.innerHTML =
      '<span class="loading-spinner me-2"></span>Processing...';

    // Show progress section
    progressSection.classList.remove("d-none");
    filmInfoSection.classList.add("d-none");

    // Clear previous alerts
    alertContainer.innerHTML = "";

    // Reset progress
    updateProgress(0, "Memulai analisis...");

    try {
      // Simulate progress steps
      updateProgress(20, "Mengakses halaman film...");
      await sleep(800);

      updateProgress(40, "Mencari link Buzzheavier...");
      await sleep(800);

      updateProgress(60, "Mengekstrak link Flashbang...");
      await sleep(800);

      updateProgress(80, "Mendapatkan informasi file...");
      await sleep(500);

      // Call API
      console.log("Sending request to API...");
      const response = await fetch("/api/get_download_info", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ film_url: filmUrl }),
      });

      console.log("Response received:", response.status);

      if (!response.ok) {
        throw new Error(`HTTP Error: ${response.status}`);
      }

      const data = await response.json();
      console.log("API Response:", data);

      if (data.success) {
        updateProgress(100, "Analisis selesai!");
        await sleep(500);

        // Store download data
        downloadData = data;

        // Populate film info
        populateFilmInfo(data);

        // Show film info section
        filmInfoSection.classList.remove("d-none");

        showAlert("Film berhasil dianalisis! Siap untuk download.", "success");
      } else {
        throw new Error(
          data.error || "Terjadi kesalahan saat menganalisis film"
        );
      }
    } catch (error) {
      console.error("Error:", error);
      showAlert(
        error.message ||
          "Terjadi kesalahan saat menganalisis film. Periksa URL dan coba lagi.",
        "danger"
      );
      progressSection.classList.add("d-none");
    } finally {
      // Re-enable form
      scrapeBtn.disabled = false;
      scrapeBtnText.innerHTML = "Analisis & Siapkan Download";
    }
  });

  // Download button handler
  downloadBtn.addEventListener("click", function () {
    if (!downloadData) {
      showAlert("Data download tidak tersedia!", "warning");
      return;
    }

    const fileName = downloadData.filename;
    const downloadUrl = downloadData.buzzheavier_link; // This is actually the flashbang link

    if (fileName && downloadUrl) {
      // Show download starting message
      downloadBtnText.innerHTML =
        '<span class="loading-spinner me-2"></span>Mempersiapkan Download...';
      downloadBtn.disabled = true;

      showAlert("Download dimulai! Periksa folder download Anda.", "info");

      // Create download link
      const downloadLink = `/download?filename=${encodeURIComponent(
        fileName
      )}&url=${encodeURIComponent(downloadUrl)}`;

      // Create invisible link and click it
      const link = document.createElement("a");
      link.href = downloadLink;
      link.target = "_blank";
      link.download = fileName;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      // Reset button after 3 seconds
      setTimeout(() => {
        downloadBtnText.innerHTML = "Download Film Sekarang";
        downloadBtn.disabled = false;
      }, 3000);
    } else {
      showAlert("Informasi download tidak lengkap!", "warning");
    }
  });

  // Helper functions
  function updateProgress(percentage, status) {
    progressBar.style.width = percentage + "%";
    progressBar.textContent = percentage + "%";
    statusText.textContent = status;
  }

  function populateFilmInfo(data) {
    console.log("Populating film info with:", data);

    // Use film_info object if available, otherwise use direct properties
    const filmInfo = data.film_info || data;

    // Set film title
    const title = filmInfo.title || data.film_title || "Unknown Movie";
    document.getElementById("filmTitle").textContent = title;

    // Set poster (with error handling)
    const posterImg = document.getElementById("filmPoster");
    const posterUrl = filmInfo.poster_url;
    if (
      posterUrl &&
      posterUrl !==
        "https://via.placeholder.com/300x450/667eea/ffffff?text=No+Poster"
    ) {
      posterImg.src = posterUrl;
      posterImg.onerror = function () {
        this.src =
          "https://via.placeholder.com/300x450/667eea/ffffff?text=Film+Poster";
      };
    } else {
      posterImg.src =
        "https://via.placeholder.com/300x450/667eea/ffffff?text=Film+Poster";
    }

    // Set rating
    const rating = parseFloat(filmInfo.rating || 0);
    updateRatingDisplay(rating);

    // Set basic info with fallbacks
    document.getElementById("releaseDate").textContent =
      filmInfo.release_date || "Unknown";
    document.getElementById("duration").textContent =
      filmInfo.duration || "Unknown";
    document.getElementById("country").textContent =
      filmInfo.country || "Unknown";
    document.getElementById("filmType").textContent = filmInfo.type || "WEB-DL";
    document.getElementById("director").textContent =
      filmInfo.director || "Unknown Director";
    document.getElementById("cast").textContent =
      filmInfo.cast || "Unknown Cast";
    document.getElementById("description").textContent =
      filmInfo.description || "No description available.";

    // Set genres
    const genresContainer = document.getElementById("genres");
    const genres = filmInfo.genres || ["Unknown"];
    genresContainer.innerHTML = "";
    genres.forEach((genre) => {
      const badge = document.createElement("span");
      badge.className = "badge genre-badge me-1";
      badge.textContent = genre;
      genresContainer.appendChild(badge);
    });

    // Set download info with enhanced file size display
    document.getElementById("fileName").textContent =
      data.filename || "movie-download.mp4";

    // Enhanced file size display
    const fileSizeElement = document.getElementById("fileSize");
    let fileSize = "Unknown";

    // Try to get file size from multiple sources
    if (data.file_size_formatted) {
      fileSize = data.file_size_formatted;
      console.log("Using file_size_formatted:", fileSize);
    } else if (data.file_size && data.file_size > 0) {
      fileSize = formatFileSize(data.file_size);
      console.log("Formatting raw file_size:", data.file_size, "->", fileSize);
    } else {
      console.log("No file size data available, using default");
      fileSize = "Calculating...";

      // Try to get size asynchronously if not available
      setTimeout(() => {
        if (data.file_size && data.file_size > 0) {
          fileSizeElement.textContent = formatFileSize(data.file_size);
        }
      }, 1000);
    }

    fileSizeElement.textContent = fileSize;

    // Add debug info to console
    console.log("File size debug info:", {
      file_size: data.file_size,
      file_size_formatted: data.file_size_formatted,
      final_display: fileSize,
    });
  }

  function updateRatingDisplay(rating) {
    const ratingContainer = document.getElementById("filmRating");
    const ratingValue = document.getElementById("ratingValue");

    // Clear existing stars
    ratingContainer.innerHTML = "";

    // Add stars based on rating
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);

    // Add full stars
    for (let i = 0; i < fullStars; i++) {
      const star = document.createElement("i");
      star.className = "fas fa-star";
      ratingContainer.appendChild(star);
    }

    // Add half star if needed
    if (hasHalfStar) {
      const halfStar = document.createElement("i");
      halfStar.className = "fas fa-star-half-alt";
      ratingContainer.appendChild(halfStar);
    }

    // Add empty stars
    for (let i = 0; i < emptyStars; i++) {
      const star = document.createElement("i");
      star.className = "far fa-star";
      ratingContainer.appendChild(star);
    }

    // Add rating value text
    const ratingSpan = document.createElement("span");
    ratingSpan.className = "ms-2 text-muted";
    ratingSpan.id = "ratingValue";
    ratingSpan.textContent = rating.toFixed(1);
    ratingContainer.appendChild(ratingSpan);
  }

  function formatFileSize(bytes) {
    console.log("formatFileSize called with:", bytes, typeof bytes);

    // Handle various input types
    let sizeBytes;
    if (typeof bytes === "string") {
      sizeBytes = parseInt(bytes);
    } else if (typeof bytes === "number") {
      sizeBytes = bytes;
    } else {
      console.log("Invalid bytes input:", bytes);
      return "Unknown";
    }

    // Check if valid number
    if (!sizeBytes || isNaN(sizeBytes) || sizeBytes <= 0) {
      console.log("Invalid file size:", sizeBytes);
      return "Unknown";
    }

    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB", "TB"];
    const i = Math.floor(Math.log(sizeBytes) / Math.log(k));

    if (i >= sizes.length) {
      return "Very Large";
    }

    const formattedSize = parseFloat((sizeBytes / Math.pow(k, i)).toFixed(2));
    const result = `${formattedSize} ${sizes[i]}`;

    console.log("Formatted size:", sizeBytes, "->", result);
    return result;
  }

  function showAlert(message, type) {
    const alertDiv = document.createElement("div");
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
          <i class="fas fa-${getAlertIcon(type)} me-2"></i>
          ${message}
          <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
      `;
    alertContainer.appendChild(alertDiv);

    // Auto-remove after 8 seconds for non-error alerts
    if (type !== "danger") {
      setTimeout(() => {
        if (alertDiv.parentNode) {
          alertDiv.remove();
        }
      }, 8000);
    }
  }

  function getAlertIcon(type) {
    const icons = {
      success: "check-circle",
      danger: "exclamation-triangle",
      warning: "exclamation-circle",
      info: "info-circle",
    };
    return icons[type] || "info-circle";
  }

  function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
});
