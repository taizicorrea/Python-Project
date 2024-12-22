document.addEventListener('DOMContentLoaded', () => {
    const existingQuestionsList = document.getElementById('existingQuestionsList');
    const questionsList = document.getElementById('questionsList'); // Ensure questions list container is defined

    // Initialize SweetAlert2 Toast
    const Toast = Swal.mixin({
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 3000,
        timerProgressBar: true
    });

    // Load existing questions from the server
    document.getElementById('loadExistingQuestionsBtn').addEventListener('click', () => {
        fetch('/get-questions/') // Replace with your Django endpoint
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to fetch questions from the server');
                }
                return response.json();
            })
            .then(data => {
                renderExistingQuestions(data.questions);
            })
            .catch(error => {
                console.error('Error fetching questions:', error);
                Toast.fire({
                    icon: 'error',
                    title: 'Failed to load existing questions!'
                });
            });
    });

    // Render existing questions in the modal
    function renderExistingQuestions(questions) {
        existingQuestionsList.innerHTML = ''; // Clear any existing content

        if (!questions || questions.length === 0) {
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
                // Prevent adding duplicate questions
                if (stagedQuestions.some(q => normalizeId(q.id) === normalizeId(question.id))) {
                    Toast.fire({
                        icon: 'warning',
                        title: 'This question is already added.'
                    });
                    return;
                }

                try {
                    // Use shared logic to add questions
                    addSharedQuestion(question);

                    Toast.fire({
                        icon: 'success',
                        title: 'Question added successfully!'
                    });
                } catch (error) {
                    console.error('Error adding question:', error);
                    Toast.fire({
                        icon: 'error',
                        title: 'Failed to add question!'
                    });
                }
            });

            existingQuestionsList.appendChild(listItem);
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
});
