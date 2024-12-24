document.addEventListener('DOMContentLoaded', function () {
    let warningCount = 0; // Counter for warnings
    const maxWarnings = 2; // Maximum warnings allowed
    const quizForm = document.getElementById('quiz-form');

    function showWarning(message) {
        warningCount++;
        Swal.fire({
            icon: 'warning',
            title: 'Warning',
            text: `${message}\nWarning ${warningCount}/${maxWarnings}`,
            confirmButtonText: 'Got it',
        }).then(() => {
            // Attempt to re-enter full-screen mode
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen().catch(err => {
                    console.error("Failed to enable full screen:", err);
                });
            }

            // Check if max warnings exceeded
            if (warningCount >= maxWarnings) {
                Swal.fire({
                    icon: 'error',
                    title: 'Quiz Submitted',
                    text: 'You have exceeded the maximum number of warnings. Your quiz will be submitted now.',
                    confirmButtonText: 'OK',
                }).then(() => {
                    autoSubmitQuiz();
                });
            }
        });
    }

    function autoSubmitQuiz() {
        // Reset all selected answers (set score to zero)
        const inputs = quizForm.querySelectorAll('input[type="radio"], input[type="text"]');
        inputs.forEach(input => {
            if (input.type === "radio") {
                input.checked = false; // Uncheck radio buttons
            } else if (input.type === "text") {
                input.value = ""; // Clear text inputs
            }
        });

        // Submit the form
        quizForm.submit();
    }

    function enforceFullScreen() {
        if (!document.fullscreenElement) {
            showWarning("You exited full screen. Please return to full screen to continue.");
        }
    }

    function monitorTabSwitch() {
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                showWarning('You switched tabs or minimized the window.');
            }
        });
    }

    function initializeAntiCheating() {
        // Enforce full-screen mode
        document.documentElement.requestFullscreen().catch(err => {
            Swal.fire({
                icon: 'error',
                title: 'Full Screen Required',
                text: 'Please enable full screen to start the quiz.',
                confirmButtonText: 'OK',
            });
        });

        // Monitor for full-screen exit
        document.addEventListener('fullscreenchange', enforceFullScreen);

        // Monitor for tab switching
        monitorTabSwitch();
    }

    // Export the function to be used in the main quiz script
    window.initializeAntiCheating = initializeAntiCheating;
});
