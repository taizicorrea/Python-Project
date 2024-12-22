// shared_questions.js
const stagedQuestions = JSON.parse(document.getElementById('questionsData').value || '[]');
const questionsDataInput = document.getElementById('questionsData');

// Update the hidden input with serialized questions data
function updateQuestionsData() {
    questionsDataInput.value = JSON.stringify(stagedQuestions);
    console.log("Updated Staged Questions:", stagedQuestions);
    toggleNoQuestionsMessage(); // Ensure message visibility is updated
}

// Utility function to normalize IDs
function normalizeId(id) {
    return typeof id === 'string' ? id : id.toString();
}

// Add a question to the UI
function addQuestionToUI(question, questionsList) {
    const questionCard = document.createElement('div');
    questionCard.classList.add('card', 'border-0', 'shadow-sm', 'p-3', 'mb-2');

    questionCard.innerHTML = `
        <div class="card-body">
            <h6 class="card-title">${question.question_text}</h6>
            <p class="card-text">
                <strong>Type:</strong> ${formatQuestionType(question.question_type)}
            </p>
            ${question.multiple_choice_options?.length
                ? `<p><strong>Options:</strong></p>
                   <ul>${question.multiple_choice_options
                       .map(option => `<li>${option}</li>`)
                       .join('')}</ul>`
                : ''}
            <p><strong>Correct Answer(s):</strong> ${
                question.correct_answers?.length
                    ? `<ul>${question.correct_answers
                          .map(answer => `<li>${answer}</li>`)
                          .join('')}</ul>`
                    : '<span class="text-muted">N/A</span>'
            }</p>
            <button type="button" class="btn btn-danger btn-sm removeQuestionBtn">Remove</button>
        </div>
    `;

    questionCard.querySelector('.removeQuestionBtn').addEventListener('click', () => {
        removeQuestionFromStaged(question, questionCard);
    });

    questionsList.appendChild(questionCard);
    toggleNoQuestionsMessage(); // Ensure message updates after adding a question
}

// Remove a question from stagedQuestions and UI
function removeQuestionFromStaged(question, questionCard) {
    const index = stagedQuestions.findIndex(q => normalizeId(q.id) === normalizeId(question.id));
    if (index > -1) {
        stagedQuestions.splice(index, 1); // Remove question from stagedQuestions
        updateQuestionsData(); // Update hidden input
    }
    questionCard.remove(); // Remove from UI

    toggleNoQuestionsMessage(); // Update visibility of "No Questions Added" message

    // Display success toast for removal
    Toast.fire({
        icon: 'info',
        title: 'Question removed successfully!'
    });
}

// Format question type for display
function formatQuestionType(type) {
    switch (type) {
        case 'multiple_choice':
            return 'Multiple Choice';
        case 'true_false':
            return 'True/False';
        case 'identification':
            return 'Identification';
        default:
            return 'Unknown Type';
    }
}

// Add a question to stagedQuestions and UI
function addSharedQuestion(question) {
    const normalizedId = normalizeId(question.id);

    // Check if the question already exists in stagedQuestions
    if (stagedQuestions.some(q => normalizeId(q.id) === normalizedId)) {
        console.warn('Duplicate question detected:', question);
        return false; // Indicate failure
    }

    stagedQuestions.push(question); // Add question to stagedQuestions
    updateQuestionsData(); // Update hidden input
    const questionsList = document.getElementById('questionsList'); // Get questions list UI
    addQuestionToUI(question, questionsList); // Add to UI
    return true; // Indicate success
}


// Toggle "No Questions Added" message visibility
function toggleNoQuestionsMessage() {
    const noQuestionsMessage = document.querySelector('.no-questions-message');
    if (noQuestionsMessage) {
        noQuestionsMessage.style.display = stagedQuestions.length === 0 ? 'block' : 'none';
    }
}

// Initialize visibility on page load
toggleNoQuestionsMessage();
