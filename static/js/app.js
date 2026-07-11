// ======================================================
// Glowise 3.0
// app.js
// Part 1
// ======================================================

// ----------------------------
// DOM Elements
// ----------------------------

const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const preview = document.getElementById("preview");

const startCameraBtn = document.getElementById("startCamera");
const captureBtn = document.getElementById("captureBtn");
const retakeBtn = document.getElementById("retakeBtn");
const analyzeBtn = document.getElementById("analyzeBtn");

const uploadInput = document.getElementById("photoInput");

const loadingCard = document.getElementById("loadingCard");
const dashboard = document.getElementById("dashboard");

// ----------------------------
// Variables
// ----------------------------

let stream = null;
let selectedBlob = null;

// ======================================================
// CAMERA
// ======================================================

async function startCamera() {

    try {

        stream = await navigator.mediaDevices.getUserMedia({

            video: {

                facingMode: "user",

                width: 1280,

                height: 720

            },

            audio: false

        });

        video.srcObject = stream;

        video.classList.remove("d-none");

        preview.classList.add("d-none");

    }

    catch (err) {

        alert("Unable to access camera.");

        console.error(err);

    }

}

// ======================================================
// OPEN CAMERA
// ======================================================

startCameraBtn.addEventListener("click", startCamera);

// ======================================================
// CAPTURE IMAGE
// ======================================================

captureBtn.addEventListener("click", () => {

    const context = canvas.getContext("2d");

    canvas.width = video.videoWidth;

    canvas.height = video.videoHeight;

    context.drawImage(

        video,

        0,

        0,

        canvas.width,

        canvas.height

    );

    canvas.toBlob(

        function(blob){

            selectedBlob = blob;

        },

        "image/jpeg",

        0.95

    );

    preview.src = canvas.toDataURL("image/jpeg");

    preview.classList.remove("d-none");

    video.classList.add("d-none");

    captureBtn.classList.add("d-none");

    retakeBtn.classList.remove("d-none");

    analyzeBtn.classList.remove("d-none");

});

// ======================================================
// RETAKE
// ======================================================

retakeBtn.addEventListener("click", () => {

    preview.classList.add("d-none");

    video.classList.remove("d-none");

    captureBtn.classList.remove("d-none");

    analyzeBtn.classList.add("d-none");

    retakeBtn.classList.add("d-none");

    selectedBlob = null;

});

// ======================================================
// IMAGE UPLOAD
// ======================================================

uploadInput.addEventListener("change", (event) => {

    const file = event.target.files[0];

    if (!file) return;

    selectedBlob = file;

    preview.src = URL.createObjectURL(file);

    preview.classList.remove("d-none");

    video.classList.add("d-none");

    analyzeBtn.classList.remove("d-none");

    retakeBtn.classList.remove("d-none");

    captureBtn.classList.add("d-none");

});
// ======================================================
// ANALYZE BUTTON
// ======================================================

analyzeBtn.addEventListener("click", analyzeFace);

async function analyzeFace() {

    if (!selectedBlob) {

        alert("Please capture or upload an image first.");

        return;

    }

    loadingCard.classList.remove("d-none");

    dashboard.classList.add("d-none");

    analyzeBtn.disabled = true;

    const formData = new FormData();

    formData.append(

        "photo",

        selectedBlob,

        "face.jpg"

    );

    formData.append(

        "city",

        "Bangalore"

    );

    try {

        const response = await fetch(

            "/api/face-analysis",

            {

                method: "POST",

                body: formData

            }

        );

        const data = await response.json();

        loadingCard.classList.add("d-none");

        analyzeBtn.disabled = false;

        if (!response.ok || !data.success) {

            throw new Error(

                data.message ||

                "Analysis failed."

            );

        }

        renderDashboard(data);

    }

    catch (error) {

        loadingCard.classList.add("d-none");

        analyzeBtn.disabled = false;

        console.error(error);

        alert(

            "Something went wrong while analyzing.\n\n" +

            error.message

        );

    }

}
// ======================================================
// RENDER DASHBOARD
// ======================================================

function renderDashboard(data) {
    console.log(data);
    dashboard.classList.remove("d-none");

    dashboard.scrollIntoView({

        behavior: "smooth"

    });

    // ----------------------------
    // Skin Score
    // ----------------------------

    document.getElementById("skinScore").textContent =
        data.skin_score || "--";

    // ----------------------------
    // Skin Type
    // ----------------------------

    const skinType = document.getElementById("skinType");

    if (skinType) {

        skinType.textContent =
            `🧴 ${data.skin_type} Skin`;

    }

    // ----------------------------
    // Summary
    // ----------------------------

    const summary = document.getElementById("summary");

    if (summary) {

        summary.textContent =
            data.summary || "No summary available.";

    }

   
    // ----------------------------
    // Concerns
    // ----------------------------

    const concernsContainer =
        document.getElementById("concerns");

    if (concernsContainer) {

        concernsContainer.innerHTML = "";

        if (
            !data.concerns ||
            data.concerns.length === 0
        ) {

            concernsContainer.innerHTML = `

            <div class="alert alert-success">

                🎉 No major skin concerns detected.

            </div>

            `;

        }

        else {

            data.concerns.forEach(concern => {

                let color = "success";

                if (concern.severity === "Medium")
                    color = "warning";

                if (concern.severity === "High")
                    color = "danger";

                concernsContainer.innerHTML += `

                <div class="card mb-3 shadow-sm">

                    <div class="card-body">

                        <h5>

                            🔍 ${concern.name}

                        </h5>

                        <span class="badge bg-${color}">

                            ${concern.severity}

                        </span>

                    </div>

                </div>

                `;

            });

        }

    }
        // ----------------------------
    // Morning Routine
    // ----------------------------

    const morningList = document.getElementById("morningList");

    if (morningList) {

        morningList.innerHTML = "";

        (data.morning || []).forEach(step => {

            morningList.innerHTML += `

                <li>${step}</li>

            `;

        });

    }

    // ----------------------------
    // Night Routine
    // ----------------------------

    const nightList = document.getElementById("nightList");

    if (nightList) {

        nightList.innerHTML = "";

        (data.night || []).forEach(step => {

            nightList.innerHTML += `

                <li>${step}</li>

            `;

        });

    }

    // ----------------------------
    // Products
    // ----------------------------

    const productCards = document.getElementById("productCards");

    if (productCards) {

        productCards.innerHTML = "";

        if (!data.products || data.products.length === 0) {

            productCards.innerHTML = `

                <div class="alert alert-secondary">

                    No products available.

                </div>

            `;

        }

        else {

            data.products.forEach(product => {

                productCards.innerHTML += `

                <div class="card mb-3 shadow-sm">

                    ${product.image ? `
<div class="product-image">
    <img
        src="${product.image}"
        class="product-img"
        alt="${product.name}">
</div>
` : ""}

                    <div class="card-body">

                        <h5 class="card-title">

                            ${product.name}

                        </h5>

                        <p class="text-success fw-bold">

                            ${product.brand || ""}

                        </p>

                        <p>

                            ${product.description || ""}

                        </p>

                        <div class="d-flex justify-content-between">

                            <span>

                                ⭐ ${product.rating || "N/A"}

                            </span>

                            <span>

                                💰 ${product.price || ""}

                            </span>

                        </div>

                    </div>

                </div>

                `;

            });

        }

    }

    // ----------------------------
    // Home Remedies
    // ----------------------------

    const remedyCards = document.getElementById("remedyCards");

    if (remedyCards) {

        remedyCards.innerHTML = "";

        if (!data.remedies || data.remedies.length === 0) {

            remedyCards.innerHTML = `

                <div class="alert alert-secondary">

                    No home remedies available.

                </div>

            `;

        }

        else {

            data.remedies.forEach(remedy => {

                remedyCards.innerHTML += `

                <div class="card border-success mb-3">

                    <div class="card-body">

                        <h5>

                            🌿 ${remedy.title}

                        </h5>

                        <p>

                            ${remedy.description}

                        </p>

                        <small class="text-muted">

                            ⏱ ${remedy.time_required || ""}

                        </small>

                        <br>

                        <small class="text-muted">

                            📅 ${remedy.frequency || ""}

                        </small>

                    </div>

                </div>

                `;

            });

        }

    }
        // ----------------------------
    // Ingredients To Use
    // ----------------------------

    const ingredientsUse = document.getElementById("ingredientsUse");

    if (ingredientsUse) {

        ingredientsUse.innerHTML = "";

        (data.ingredients_to_use || []).forEach(item => {

            ingredientsUse.innerHTML += `

                <li>✅ ${item}</li>

            `;

        });

    }

    // ----------------------------
    // Ingredients To Avoid
    // ----------------------------

    const ingredientsAvoid = document.getElementById("ingredientsAvoid");

    if (ingredientsAvoid) {

        ingredientsAvoid.innerHTML = "";

        (data.ingredients_to_avoid || []).forEach(item => {

            ingredientsAvoid.innerHTML += `

                <li>❌ ${item}</li>

            `;

        });

    }

  

    // ----------------------------
    // Weather
    // ----------------------------

    const weatherCard = document.getElementById("weatherCard");

    if (weatherCard && data.weather) {

        weatherCard.innerHTML = `

        <div class="row text-center">

            <div class="col-md-4">

                <h5>📍 ${data.weather.city || "Unknown"}</h5>

            </div>

            <div class="col-md-4">

                <h5>🌡 ${data.weather.temperature ?? "--"}°C</h5>

            </div>

            <div class="col-md-4">

                <h5>💧 ${data.weather.humidity ?? "--"}%</h5>

            </div>

        </div>

        <hr>

        <p class="text-center">

            ${data.weather.description || ""}

        </p>

        `;

    }

    // ----------------------------
    // Finished Rendering
    // ----------------------------

    dashboard.classList.remove("d-none");

    dashboard.scrollIntoView({

        behavior: "smooth"

    });

}
// ======================================================
// RESET DASHBOARD
// ======================================================

function resetDashboard() {

    dashboard.classList.add("d-none");

    const ids = [

        "analysisText",
        "morningList",
        "nightList",
        "productCards",
        "remedyCards",
        "ingredientsUse",
        "ingredientsAvoid",
        "lifestyle",
        "weatherCard",
        "concerns"

    ];

    ids.forEach(id => {

        const element = document.getElementById(id);

        if (element) {

            element.innerHTML = "";

        }

    });

    const score = document.getElementById("skinScore");

    if (score) {

        score.textContent = "--";

    }

    const skinType = document.getElementById("skinType");

    if (skinType) {

        skinType.textContent = "";

    }

    const summary = document.getElementById("summary");

    if (summary) {

        summary.textContent = "";

    }

}


// ======================================================
// RESET WHEN NEW IMAGE IS CHOSEN
// ======================================================

uploadInput.addEventListener("change", resetDashboard);

retakeBtn.addEventListener("click", resetDashboard);


// ======================================================
// STOP CAMERA WHEN PAGE CLOSES
// ======================================================

window.addEventListener("beforeunload", () => {

    if (!stream) return;

    stream.getTracks().forEach(track => {

        track.stop();

    });

});


// ======================================================
// OPTIONAL: AUTO START CAMERA
// ======================================================

window.addEventListener("load", () => {

    if (

        navigator.mediaDevices &&

        navigator.mediaDevices.getUserMedia

    ) {

        startCamera();

    }

});


// ======================================================
// GLOWISE READY
// ======================================================

console.log("🌿 Glowise 3.0 Loaded Successfully");