document.addEventListener('DOMContentLoaded', () => {
    const existingQuestionsList = document.getElementById('existingQuestionsList');
    const questionsList = document.getElementById('questionsList');

    // Initialize SweetAlert2 Toast
    const Toast = Swal.mixin({
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 3000,
        timerProgressBar: true
    });

    // Load existing questions
    document.getElementById('loadExistingQuestionsBtn').addEventListener('click', () => {
        fetch('/get-questions/') // Replace with your Django URL
            .then(response => response.json())
            .then(data => {
                renderExistingQuestions(data.questions);
            })
            .catch(error => console.error('Error fetching questions:', error));
    });

    // Render existing questions in the modal
    function renderExistingQuestions(questions) {
        existingQuestionsList.innerHTML = ''; // Clear existing content

        if (questions.length === 0) {
            existingQuestionsList.innerHTML = '<p class="text-muted">No questions available in the question bank.</p>';
            return;
        }

        questions.forEach(question => {
            question.multiple_choice_options = question.multiple_choice_options || [];
            question.correct_answers = question.correct_answers || [];

            const listItem = document.createElement('li');
            listItem.classList.add('list-group-item');
            listItem.innerHTML = `
                <p><strong>${question.question_text}</strong></p>
                <p>Type: ${formatQuestionType(question.question_type)}</p>
                <button type="button" class="btn btn-primary btn-sm addQuestionBtn">Add</button>
            `;

            listItem.querySelector('.addQuestionBtn').addEventListener('click', () => {
                if (stagedQuestions.some(q => normalizeId(q.id) === normalizeId(question.id))) {
                    Toast.fire({
                        icon: 'warning',
                        title: 'This question is already added.'
                    });
                    return;
                }

                stagedQuestions.push(question); // Add to staged questions
                updateQuestionsData(); // Update shared staged questions
                addQuestionToUI(question, questionsList, toggleNoQuestionsMessage); // Use shared UI logic
                toggleNoQuestionsMessage(); // Update the "No Questions" message visibility
                Toast.fire({
                    icon: 'success',
                    title: 'Question added successfully!'
                });
            });

            existingQuestionsList.appendChild(listItem);
        });
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

    // Toggle "No Questions" message visibility using shared functionality
    function toggleNoQuestionsMessage() {
        const noQuestionsMessage = document.querySelector('.no-questions-message');
        noQuestionsMessage.style.display = stagedQuestions.length === 0 ? 'block' : 'none';
    }

    toggleNoQuestionsMessage(); // Initialize message visibility
});
