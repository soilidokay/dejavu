const audio = document.getElementById("shared-audio") ?? document.createElement("audio");
audio.id = "shared-audio";
audio.style.display = "none";
let currentProgress = null;
let currentBtn = null;
let startTime = 0;
let endTime = 0;
let interval = null;
let audioId = '';

document.addEventListener("click", (e) => {
    // Phát âm thanh
    if (e.target.classList.contains("play-button")) {
        const btn = e.target;

        const file = btn.dataset.file;
        startTime = parseFloat(btn.dataset.start);
        endTime = parseFloat(btn.dataset.end);
        const progressId = btn.dataset.id;

        const container = document.querySelector(`.progress-container[data-id="${progressId}"]`);
        currentProgress = container.querySelector(".progress");

        if (currentBtn && currentBtn !== btn) {
            currentBtn.innerText = "▶️ Phát";
        }

        // Nếu đang phát lại đúng đoạn thì dừng
        if ((audio.src === file || audioId == progressId) && !audio.paused) {
            audio.pause();
            btn.innerText = "▶️ Phát";
            clearInterval(interval);
            return;
        }

        audioId = progressId;
        // Nếu không thì phát lại đoạn mới
        audio.src = file;
        audio.currentTime = startTime;
        audio.play();
        btn.innerText = "⏸ Dừng";
        currentBtn = btn;

        clearInterval(interval);
        interval = setInterval(() => {
            if (audio.currentTime >= endTime) {
                audio.pause();
                btn.innerText = "▶️ Phát";
                clearInterval(interval);
                if (currentProgress) currentProgress.style.width = "0%";
            } else {
                const percent = ((audio.currentTime - startTime) / (endTime - startTime)) * 100;
                if (currentProgress) currentProgress.style.width = percent + "%";
            }
        }, 100);
    }

    // Tua khi click progress
    if (e.target.classList.contains("progress-container")) {
        const container = e.target;
        const progress = container.querySelector(".progress");
        const id = container.dataset.id;

        if (!progress || !currentProgress || id !== currentProgress.closest(".progress-container").dataset.id) {
            return; // Không phải đoạn đang phát
        }

        const rect = container.getBoundingClientRect();
        const percent = (e.clientX - rect.left) / rect.width;
        const newTime = startTime + (endTime - startTime) * percent;

        audio.currentTime = newTime;
        progress.style.width = percent * 100 + "%";
    }
});

// Dừng cập nhật khi pause
audio.addEventListener("pause", () => {
    clearInterval(interval);
    if (currentBtn) currentBtn.innerText = "▶️ Phát";
});