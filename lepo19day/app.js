document.addEventListener("DOMContentLoaded", () => {
    // Audio Autoplay
    const audio = document.getElementById("bg-audio");
    if (audio) {
        audio.volume = 0.6;
        const tryPlay = () => {
            audio.play().then(() => {
                ["click", "mousemove", "pointerdown", "scroll", "keydown", "touchstart"].forEach(evt => {
                    window.removeEventListener(evt, tryPlay);
                });
            }).catch(() => {});
        };

        tryPlay();

        ["click", "mousemove", "pointerdown", "scroll", "keydown", "touchstart"].forEach(evt => {
            window.addEventListener(evt, tryPlay, { once: false });
        });
    }

    // Render Scattered Photos below Folders
    renderScatteredArcPhotos();

    // Attach 3D tilt listener to modal card
    init3DTilt();
});

// Interactive Photo Click on Folder Covers
function handlePhotoClick(event, frameEl) {
    event.stopPropagation(); // prevent folder open

    if (!frameEl.classList.contains("tape-removed")) {
        frameEl.classList.add("tape-peeling");
        setTimeout(() => {
            frameEl.classList.add("tape-removed");
            frameEl.classList.remove("tape-peeling");
        }, 400);
    } else {
        frameEl.classList.toggle("flipped");
    }
}

// Render Scattered Photos Below Folders
function renderScatteredArcPhotos() {
    const grid = document.getElementById("scattered-arc-grid");
    if (!grid || typeof arcData === 'undefined') return;

    grid.innerHTML = "";

    arcData.forEach((item) => {
        const polaroid = document.createElement("div");
        polaroid.className = "scattered-polaroid-item";

        // Organic random tilt & offset
        const rot = (Math.random() - 0.5) * 28; // -14deg to +14deg
        const offsetY = (Math.random() - 0.5) * 16;
        polaroid.style.transform = `rotate(${rot}deg) translateY(${offsetY}px)`;

        // Tape strap
        const tape = document.createElement("div");
        tape.className = "tape-strap top-center";
        polaroid.appendChild(tape);

        // Photo frame
        const imgWrap = document.createElement("div");
        imgWrap.className = "polaroid-img-wrap";

        const img = document.createElement("img");
        img.src = item.file;
        img.alt = "Photo memory";
        img.loading = "lazy";
        imgWrap.appendChild(img);

        polaroid.appendChild(imgWrap);

        // Click event to trigger 3D rising modal
        polaroid.addEventListener("click", (e) => {
            e.stopPropagation();
            openPhoto3D(item);
        });

        grid.appendChild(polaroid);
    });
}

// Open Folder View
function openFolder(event, category) {
    if (event) event.stopPropagation();
    
    const modal = document.getElementById("folder-modal");
    const deskInner = document.getElementById("opened-folder-desk");
    const canvas = document.getElementById("envelopes-canvas");

    if (modal) modal.classList.remove("closing");
    if (deskInner) deskInner.classList.remove("closing");

    const filtered = memorandumData.filter(item => item.category === category);
    canvas.innerHTML = "";

    modal.classList.add("active");

    requestAnimationFrame(() => {
        const isMobile = window.innerWidth <= 768;
        const envWidth = isMobile ? 85 : 125;
        const envHeight = isMobile ? 56 : 82;

        const canvasWidth = canvas.clientWidth || 320;
        const canvasHeight = canvas.clientHeight || 340;

        const total = filtered.length;

        // Grid layout
        let cols = 2;
        if (total > 6) cols = 3;
        if (total > 9) cols = 4;
        const rows = Math.ceil(total / cols);

        const clusterW = Math.min(canvasWidth * 0.75, cols * envWidth + (cols - 1) * 20);
        const clusterH = Math.min(canvasHeight * 0.75, rows * envHeight + (rows - 1) * 15);

        const startX = (canvasWidth - clusterW) / 2;
        const startY = (canvasHeight - clusterH) / 2;

        const stepX = cols > 1 ? (clusterW - envWidth) / (cols - 1) : 0;
        const stepY = rows > 1 ? (clusterH - envHeight) / (rows - 1) : 0;

        filtered.forEach((item, index) => {
            const env = document.createElement("div");
            env.className = "mini-envelope";
            
            const row = Math.floor(index / cols);
            const col = index % cols;

            const baseX = startX + col * stepX;
            const baseY = startY + row * stepY;

            const offsetX = (Math.random() - 0.5) * (isMobile ? 12 : 22);
            const offsetY = (Math.random() - 0.5) * (isMobile ? 12 : 22);
            const randomRotation = (Math.random() - 0.5) * 34;

            const finalX = Math.max(10, Math.min(canvasWidth - envWidth - 10, baseX + offsetX));
            const finalY = Math.max(10, Math.min(canvasHeight - envHeight - 10, baseY + offsetY));

            env.style.left = `${finalX}px`;
            env.style.top = `${finalY}px`;
            env.style.transform = `rotate(${randomRotation}deg)`;

            const flap = document.createElement("div");
            flap.className = "mini-envelope-flap";
            env.appendChild(flap);

            const initials = document.createElement("span");
            initials.className = "mini-envelope-initials";
            initials.textContent = item.initials || item.name.slice(0, 2).toUpperCase();
            env.appendChild(initials);

            env.addEventListener("click", (e) => {
                e.stopPropagation();
                openLetter(item);
            });

            canvas.appendChild(env);
        });
    });
}

function closeFolder() {
    const modal = document.getElementById("folder-modal");
    const deskInner = document.getElementById("opened-folder-desk");

    if (modal && modal.classList.contains("active")) {
        modal.classList.add("closing");
        if (deskInner) deskInner.classList.add("closing");

        setTimeout(() => {
            modal.classList.remove("active");
            modal.classList.remove("closing");
            if (deskInner) deskInner.classList.remove("closing");
        }, 320);
    }
}

// Open Letter
function openLetter(item) {
    const modal = document.getElementById("letter-modal");
    const bodyEl = document.getElementById("letter-body");
    const senderEl = document.getElementById("letter-sender");
    const mediaContainer = document.getElementById("letter-media-container");

    if (senderEl) {
        senderEl.textContent = `From: ${item.name}`;
    }
    bodyEl.textContent = item.message;

    mediaContainer.innerHTML = "";
    if (item.media) {
        if (item.mediaType === 'video') {
            const video = document.createElement("video");
            video.src = item.media;
            video.controls = true;
            video.autoplay = true;
            mediaContainer.appendChild(video);
        } else {
            const img = document.createElement("img");
            img.src = item.media;
            img.alt = `${item.name}'s photo`;
            img.onerror = () => { img.style.display = 'none'; };
            mediaContainer.appendChild(img);
        }
    }

    modal.classList.add("active");
}

function closeLetter() {
    const modal = document.getElementById("letter-modal");
    modal.classList.remove("active");
    const mediaContainer = document.getElementById("letter-media-container");
    if (mediaContainer) {
        const video = mediaContainer.querySelector("video");
        if (video) video.pause();
    }
}

// 3D Rising Photo Modal Logic
function openPhoto3D(item) {
    const modal = document.getElementById("photo-modal-3d");
    const imgEl = document.getElementById("photo-3d-img");
    const card = document.getElementById("photo-3d-card");

    imgEl.src = item.file;

    // Reset card tilt
    card.style.transform = "perspective(1000px) rotateX(0deg) rotateY(0deg) scale(1)";

    modal.classList.add("active");
}

function closePhoto3D() {
    const modal = document.getElementById("photo-modal-3d");
    modal.classList.remove("active");
}

// 3D Interactive Tilt Handler
function init3DTilt() {
    const wrapper = document.getElementById("photo-3d-wrapper");
    const card = document.getElementById("photo-3d-card");
    if (!wrapper || !card) return;

    let bounds = null;

    const handleMove = (clientX, clientY) => {
        if (!document.getElementById("photo-modal-3d").classList.contains("active")) return;
        bounds = wrapper.getBoundingClientRect();
        
        const centerX = bounds.left + bounds.width / 2;
        const centerY = bounds.top + bounds.height / 2;

        const percentX = (clientX - centerX) / (bounds.width / 2);
        const percentY = (clientY - centerY) / (bounds.height / 2);

        // Calculate max 25 degree tilt
        const rotateY = percentX * 24; 
        const rotateX = -percentY * 24;

        card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.04)`;
    };

    wrapper.addEventListener("mousemove", (e) => {
        handleMove(e.clientX, e.clientY);
    });

    wrapper.addEventListener("touchmove", (e) => {
        if (e.touches.length > 0) {
            handleMove(e.touches[0].clientX, e.touches[0].clientY);
        }
    });

    const resetTilt = () => {
        card.style.transform = "perspective(1000px) rotateX(0deg) rotateY(0deg) scale(1)";
    };

    wrapper.addEventListener("mouseleave", resetTilt);
    wrapper.addEventListener("touchend", resetTilt);
}
