// shared_questions.js
const stagedQuestions = JSON.parse(document.getElementById('questionsData').value || '[]');
const questionsDataInput = document.getElementById('questionsData');

// Update the hidden input with serialized questions data
function updateQuestionsData() {
    questionsDataInput.value = JSON.stringify(stagedQuestions);
    console.log("Updated Staged Questions:", stagedQuestions);
}

// Utility function to normalize IDs
function normalizeId(id) {
    return typeof id === 'string' ? id : id.toString();
}

// Add a question to the UI
function addQuestionToUI(question, questionsList, toggleNoQuestionsMessage) {
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
        const index = stagedQuestions.findIndex(q => normalizeId(q.id) === normalizeId(question.id));
        if (index > -1) {
            stagedQuestions.splice(index, 1);
            updateQuestionsData();
        }
        questionCard.remove();
        toggleNoQuestionsMessage();

        // Display success toast for removal
        Toast.fire({
            icon: 'info',
            title: 'Question removed successfully!'
        });
    });

    questionsList.appendChild(questionCard);
}

// Format question type for display
function formatQuestionType(type) {
    switch (type) {
        case 'multiple_choice': return 'Multiple Choice';
        case 'true_false': return 'True/False';
        case 'identification': return 'Identification';
        default: return 'Unknown Type';
    }
}
