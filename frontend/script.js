// Replace this with your deployed backend URL later
const BACKEND = "https://REPLACE_WITH_BACKEND_URL"; 

function qs(id){ return document.getElementById(id); }

async function uploadTo(endpoint) {
  const fileInput = qs("fileInput");
  const out = qs("output");
  const imagesDiv = qs("images");
  imagesDiv.innerHTML = "";
  out.textContent = "Working...";

  if (!fileInput.files || fileInput.files.length === 0) {
    alert("Please choose a file first");
    return;
  }

  const fd = new FormData();
  fd.append("file", fileInput.files[0]);

  try {
    const res = await fetch(BACKEND + endpoint, { method: "POST", body: fd });
    const data = await res.json();
    if (!res.ok) {
      out.textContent = "Error: " + JSON.stringify(data, null, 2);
      return;
    }
    out.textContent = JSON.stringify(data, null, 2);

    if (data.images) {
      data.images.forEach(rel => {
        const img = document.createElement("img");
        img.src = BACKEND + rel;
        imagesDiv.appendChild(img);
      });
    }
    if (data.png_url) {
      const img = document.createElement("img");
      img.src = BACKEND + data.png_url;
      imagesDiv.appendChild(img);
    }
  } catch (err) {
    out.textContent = "Request failed: " + String(err);
  }
}

qs("pdfToJpgBtn").addEventListener("click", () => uploadTo("/pdf-to-jpg"));
qs("ocrBtn").addEventListener("click", () => uploadTo("/ocr"));
qs("jpgToPngBtn").addEventListener("click", () => uploadTo("/jpg-to-png"));
