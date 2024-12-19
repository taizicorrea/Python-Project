document.addEventListener('DOMContentLoaded', () => {
    const questionsList = document.getElementById('questionsList');
    const stagedQuestions = [];
    let emptyStateMessage = document.querySelector('.no-questions-message');

    // Create the empty state message if it doesn't exist
    if (!emptyStateMessage) {
        emptyStateMessage = document.createElement('div');
        emptyStateMessage.textContent = "No questions added yet.";
        emptyStateMessage.classList.add('text-center', 'text-muted', 'my-3', 'no-questions-message');
        questionsList.appendChild(emptyStateMessage);
    }

    // Function to update the empty state message
    function updateEmptyState() {
        if (stagedQuestions.length === 0) {
            emptyStateMessage.style.display = 'block'; // Show the empty state message
        } else {
            emptyStateMessage.style.display = 'none'; // Hide the empty state message
        }
    }

    // Example: Add Question to the Questions List
    function addQuestionToQuiz(question) {
        if (stagedQuestions.some(q => q.id === question.id)) {
            alert("This question has already been added.");
            return;
        }

        stagedQuestions.push(question);

        const questionCard = document.createElement('div');
        questionCard.classList.add('card', 'p-3', 'shadow-sm');
        questionCard.innerHTML = `
            <div class="card-body">
                <h6 class="card-title">${question.question_text}</h6>
                <p class="card-text text-muted">
                    Type: ${question.question_type === 'multiple_choice' ? 'Multiple Choice' : question.question_type === 'true_false' ? 'True/False' : 'Identification'}
                </p>
                ${
                    question.multiple_choice_options && question.multiple_choice_options.length > 0
                        ? `<ul>${question.multiple_choice_options.map(option => `<li>${option}</li>`).join('')}</ul>`
                        : ''
                }
                <button type="button" class="btn btn-danger btn-sm removeQuestionBtn" data-id="${question.id}">
                    Remove
                </button>
            </div>
        `;

        questionsList.appendChild(questionCard);

        // Add remove button logic
        questionCard.querySelector('.removeQuestionBtn').addEventListener('click', () => {
            const index = stagedQuestions.findIndex(q => q.id === question.id);
            if (index !== -1) {
                stagedQuestions.splice(index, 1);
            }
            questionCard.remove();
            updateEmptyState();
            alert(`Question "${question.question_text}" removed from the quiz.`);
        });

        updateEmptyState();
    }

    // Initial empty state update
    updateEmptyState();
});
