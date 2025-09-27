// Use your deployed backend URL
const BACKEND = "https://pdf-image-converter-1.onrender.com";

function qs(id) {
  return document.getElementById(id);
}

async function uploadTo(endpoint) {
  const fileInput = qs("fileInput");
  const out = qs("output");
  const imagesDiv = qs("images");
  imagesDiv.innerHTML = "";
  out.textContent = "Working...";

  if (!fileInput.files || fileInput.files.length === 0) {
    alert("Please choose a file first");
    out.textContent = "";
    return;
  }

  const fd = new FormData();
  fd.append("file", fileInput.files[0]);

  try {
    const res = await fetch(BACKEND + endpoint, {
      method: "POST",
      body: fd
    });

    const data = await res.json();

    if (!res.ok) {
      out.textContent = "Error: " + JSON.stringify(data, null, 2);
      return;
    }

    out.textContent = JSON.stringify(data, null, 2);

    // Display images if returned
    if (data.images) {
      data.images.forEach(rel => {
        const img = document.createElement("img");
        img.src = BACKEND + rel;
        img.style.maxWidth = "300px";
        img.style.margin = "5px";
        imagesDiv.appendChild(img);
      });
    }

    if (data.png_url) {
      const img = document.createElement("img");
      img.src = BACKEND + data.png_url;
      img.style.maxWidth = "300px";
      img.style.margin = "5px";
      imagesDiv.appendChild(img);
    }
  } catch (err) {
    out.textContent = "Request failed: " + String(err);
  }
}

// Button event listeners
qs("pdfToJpgBtn").addEventListener("click", () => uploadTo("/pdf-to-jpg"));
qs("ocrBtn").addEventListener("click", () => uploadTo("/ocr"));
qs("jpgToPngBtn").addEventListener("click", () => uploadTo("/jpg-to-png"));
