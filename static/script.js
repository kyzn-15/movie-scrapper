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
