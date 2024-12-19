 document.getElementById('quiz_timer').addEventListener('input', function (e) {
        const timerPreview = document.getElementById('timer-preview');
        const minutes = parseInt(e.target.value, 10);

        if (isNaN(minutes) || minutes <= 0) {
            timerPreview.textContent = '00:00';
            return;
        }

        // Update timer preview (converts minutes to HH:MM format)
        timerPreview.textContent = `${String(minutes).padStart(2, '0')}:00`;
    });