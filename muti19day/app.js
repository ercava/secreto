document.addEventListener("DOMContentLoaded", () => {
    // Populate bottom Z message
    const zMsgEl = document.getElementById("z-message");
    if (zMsgEl && typeof zLetterData !== 'undefined') {
        zMsgEl.textContent = zLetterData.message;
    }

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

    // Close bottom envelope when clicking outside of it
    document.addEventListener("click", (e) => {
        const envelope = document.getElementById("bottom-envelope");
        if (envelope && envelope.classList.contains("open")) {
            if (!envelope.contains(e.target)) {
                envelope.classList.remove("open");
            }
        }
    });
});

// Interactive Photo Click: Peel Plaster Tape First, then Flip
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

// Open Folder View with Compact Natural Envelope Cluster
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

        // Determine compact grid layout
        let cols = 2;
        if (total > 6) cols = 3;
        if (total > 9) cols = 4;
        const rows = Math.ceil(total / cols);

        // Center the cluster inside the canvas with compact spacing
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

            // Natural organic jitter and tilt
            const offsetX = (Math.random() - 0.5) * (isMobile ? 12 : 22);
            const offsetY = (Math.random() - 0.5) * (isMobile ? 12 : 22);
            const randomRotation = (Math.random() - 0.5) * 34; // -17deg to +17deg

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

// Guaranteed Folder Close Animation
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

// Open Individual Letter
function openLetter(item) {
    const modal = document.getElementById("letter-modal");
    const bodyEl = document.getElementById("letter-body");
    const mediaContainer = document.getElementById("letter-media-container");

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

// Toggle Bottom Envelope
function toggleBottomEnvelope(event) {
    if (event) event.stopPropagation();
    const envelope = document.getElementById("bottom-envelope");
    if (envelope) {
        envelope.classList.toggle("open");
    }
}
