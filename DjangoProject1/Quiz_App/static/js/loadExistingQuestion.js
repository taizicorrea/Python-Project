document.addEventListener('DOMContentLoaded', () => {
    const loadExistingQuestionsBtn = document.getElementById('loadExistingQuestionsBtn');
    const existingQuestionsList = document.getElementById('existingQuestionsList');
    const questionsList = document.getElementById('questionsList'); // The Questions Added section

    const stagedQuestions = []; // Array to track added questions

    // Fetch existing questions from the server
    loadExistingQuestionsBtn.addEventListener('click', () => {
        fetch('/get-questions/') // Ensure the URL matches your Django URLs
            .then(response => response.json())
            .then(data => {
                renderExistingQuestions(data.questions);
            })
            .catch(error => console.error('Error fetching questions:', error));
    });

    // Render the existing questions in the modal
    function renderExistingQuestions(questions) {
        existingQuestionsList.innerHTML = ''; // Clear the list
        questions.forEach(question => {
            const listItem = createExistingQuestionItem(question);
            existingQuestionsList.appendChild(listItem);
        });
    }

    // Create an individual question item for the existing questions modal
    function createExistingQuestionItem(question) {
        const listItem = document.createElement('li');
        listItem.classList.add('list-group-item');
        listItem.innerHTML = `
            <div class="mb-2">
                <strong>Question:</strong> ${question.question_text}<br>
                <strong>Type:</strong> ${formatQuestionType(question.question_type)}<br>
                ${question.multiple_choice_options?.length
                    ? `<strong>Options:</strong><ul>${question.multiple_choice_options.map(option => `<li>${option}</li>`).join('')}</ul>`
                    : ''}
                ${question.correct_answers?.length
                    ? `<strong>Correct Answer(s):</strong><ul>${question.correct_answers.map(answer => `<li>${answer}</li>`).join('')}</ul>`
                    : ''}
            </div>
            <button type="button" class="btn btn-primary btn-sm addQuestionBtn" data-id="${question.id}">Add</button>
        `;

        // Add logic to handle the "Add" button click
        listItem.querySelector('.addQuestionBtn').addEventListener('click', () => addQuestionToQuiz(question));

        return listItem;
    }

    // Add the selected question to the "Questions Added" section
    function addQuestionToQuiz(question) {
        if (stagedQuestions.some(q => q.id === question.id)) {
            alert("This question has already been added.");
            return;
        }

        // Append the question to the stagedQuestions array
        stagedQuestions.push(question);

        // Create and render the question card
        const questionCard = createQuestionCard(question);
        questionsList.appendChild(questionCard);

        alert(`Question "${question.question_text}" added to the quiz!`);
    }

    // Create a card for the "Questions Added" section
    function createQuestionCard(question) {
        const questionCard = document.createElement('div');
        questionCard.classList.add('card', 'border-0', 'shadow-sm', 'p-3', 'mb-2');

        questionCard.innerHTML = `
            <div class="card-body">
                <h6 class="card-title">${question.question_text}</h6>
                <p class="card-text">
                    <strong>Type:</strong> ${formatQuestionType(question.question_type)}<br>
                    ${question.multiple_choice_options?.length
                        ? `<strong>Options:</strong><ul>${question.multiple_choice_options.map(option => `<li>${option}</li>`).join('')}</ul>`
                        : ''}
                    ${question.correct_answers?.length
                        ? `<strong>Correct Answer(s):</strong><ul>${question.correct_answers.map(answer => `<li>${answer}</li>`).join('')}</ul>`
                        : '<strong>Correct Answer(s):</strong> <span class="text-muted">N/A</span>'}
                </p>
                <button type="button" class="btn btn-danger btn-sm removeQuestionBtn">Remove</button>
            </div>
        `;

        // Add logic to handle the "Remove" button click
        questionCard.querySelector('.removeQuestionBtn').addEventListener('click', () => removeQuestionFromQuiz(question.id, questionCard));

        return questionCard;
    }

    // Remove the question from the "Questions Added" section
    function removeQuestionFromQuiz(questionId, questionCard) {
        // Remove from the stagedQuestions array
        const index = stagedQuestions.findIndex(q => q.id === questionId);
        if (index !== -1) {
            stagedQuestions.splice(index, 1); // Remove the question
        }

        // Remove from the DOM
        questionCard.remove();

        alert(`Question removed from the quiz.`);
    }

    // Format the question type for display
    function formatQuestionType(type) {
        if (type === 'multiple_choice') return 'Multiple Choice';
        if (type === 'true_false') return 'True/False';
        if (type === 'identification') return 'Identification';
        return 'Unknown Type';
    }
});
