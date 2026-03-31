document.addEventListener('DOMContentLoaded', function () {
    const timerDiv = document.getElementById('timer');
    if (!timerDiv) return;

    const limit = parseInt(timerDiv.dataset.limit);
    const startedAt = parseInt(timerDiv.dataset.started);

    if (!limit || limit === 0) {
        timerDiv.textContent = 'No time limit';
        return;
    }

    const now = Math.floor(Date.now() / 1000);
    let remaining = limit - (now - startedAt);

    if (remaining <= 0) {
        document.querySelector('form').submit();
        return;
    }

    function updateTimer() {
        if (remaining <= 0) {
            document.querySelector('form').submit();
            return;
        }
        const minutes = Math.floor(remaining / 60);
        const seconds = remaining % 60;
        timerDiv.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        remaining--;
    }

    updateTimer();
    setInterval(updateTimer, 1000);
});