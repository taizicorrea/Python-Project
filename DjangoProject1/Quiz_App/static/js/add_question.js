document.addEventListener('DOMContentLoaded', () => {
    const questionTypeDropdown = document.getElementById('question_type');
    const questionTypeSpecificFields = document.getElementById('questionTypeSpecificFields');
    const saveQuestionBtn = document.getElementById('saveQuestionBtn');
    const questionsList = document.getElementById('questionsList'); // Ensure this is correctly defined
    const noQuestionsMessage = document.querySelector('.no-questions-message');

    // Initialize SweetAlert2 Toast
    const Toast = Swal.mixin({
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 3000,
        timerProgressBar: true
    });

    // Render specific fields based on the question type
    questionTypeDropdown.addEventListener('change', () => {
        renderQuestionFields(questionTypeDropdown.value);
    });

    // Render specific fields based on the question type
    function renderQuestionFields(type) {
        questionTypeSpecificFields.innerHTML = '';

        if (type === 'multiple_choice') {
            questionTypeSpecificFields.innerHTML = `
                <div class="mb-3">
                    <label for="options" class="form-label">Options</label>
                    <div id="optionsContainer"></div>
                    <button type="button" id="addOptionBtn" class="btn btn-sm btn-secondary mt-2">Add Option</button>
                </div>
                <div class="mb-3">
                    <label for="correct_answer" class="form-label">Correct Answer</label>
                    <input type="text" id="correct_answer" class="form-control" placeholder="Enter correct answer">
                </div>
            `;
            setupAddOption();
        } else if (type === 'true_false') {
            questionTypeSpecificFields.innerHTML = `
                <div class="mb-3">
                    <label for="correct_answer" class="form-label">Correct Answer</label>
                    <select id="correct_answer" class="form-select">
                        <option value="True">True</option>
                        <option value="False">False</option>
                    </select>
                </div>
            `;
        } else if (type === 'identification') {
            questionTypeSpecificFields.innerHTML = `
                <div class="mb-3">
                    <label for="answersContainer" class="form-label">Correct Answers</label>
                    <div id="answersContainer"></div>
                    <button type="button" id="addAnswerBtn" class="btn btn-sm btn-secondary mt-2">Add Answer</button>
                </div>
            `;
            setupAddAnswer();
        }
    }

    // Setup "Add Option" for multiple choice
    function setupAddOption() {
        const addOptionBtn = document.getElementById('addOptionBtn');
        const optionsContainer = document.getElementById('optionsContainer');

        addOptionBtn.addEventListener('click', () => {
            const optionWrapper = document.createElement('div');
            optionWrapper.classList.add('d-flex', 'mb-2');
            optionWrapper.innerHTML = `
                <input type="text" class="form-control me-2 option-input" placeholder="Enter option">
                <button type="button" class="btn btn-danger btn-sm removeOption">Remove</button>
            `;
            optionWrapper.querySelector('.removeOption').addEventListener('click', () => optionWrapper.remove());
            optionsContainer.appendChild(optionWrapper);
        });
    }

    // Setup "Add Answer" for identification
    function setupAddAnswer() {
        const addAnswerBtn = document.getElementById('addAnswerBtn');
        const answersContainer = document.getElementById('answersContainer');

        addAnswerBtn.addEventListener('click', () => {
            const answerWrapper = document.createElement('div');
            answerWrapper.classList.add('d-flex', 'mb-2');
            answerWrapper.innerHTML = `
                <input type="text" class="form-control me-2 answer-input" placeholder="Enter answer">
                <button type="button" class="btn btn-danger btn-sm removeAnswer">Remove</button>
            `;
            answerWrapper.querySelector('.removeAnswer').addEventListener('click', () => answerWrapper.remove());
            answersContainer.appendChild(answerWrapper);
        });
    }

    // Save question
    saveQuestionBtn.addEventListener('click', () => {
        const questionTextInput = document.getElementById('question_text');
        const questionText = questionTextInput.value.trim();
        const questionType = questionTypeDropdown.value;

        let correctAnswers = [];
        let options = [];

        if (questionType === 'identification') {
            correctAnswers = Array.from(document.querySelectorAll('.answer-input'))
                .map(input => input.value.trim())
                .filter(answer => answer !== '');
        } else if (questionType === 'multiple_choice') {
            options = Array.from(document.querySelectorAll('.option-input'))
                .map(input => input.value.trim())
                .filter(option => option !== '');
            correctAnswers = [document.getElementById('correct_answer').value.trim()];
        } else if (questionType === 'true_false') {
            correctAnswers = [document.getElementById('correct_answer').value.trim()];
        }

        if (!questionText || correctAnswers.length === 0 || (questionType === 'multiple_choice' && options.length === 0)) {
            Toast.fire({
                icon: 'error',
                title: 'Please fill out all required fields!'
            });
            return;
        }

        const newQuestion = {
            id: `temp-${Date.now()}`,
            question_text: questionText,
            question_type: questionType,
            multiple_choice_options: options,
            correct_answers: correctAnswers,
        };

        addQuestionToUI(newQuestion, questionsList, toggleNoQuestionsMessage); // Add to UI using shared logic
        stagedQuestions.push(newQuestion); // Add to staged questions
        updateQuestionsData(); // Update shared staged questions data

        Toast.fire({
            icon: 'success',
            title: 'Question added successfully!'
        });

        questionTextInput.value = '';
        if (questionType === 'multiple_choice') {
            document.getElementById('optionsContainer').innerHTML = '';
        } else if (questionType === 'identification') {
            document.getElementById('answersContainer').innerHTML = '';
        }

        const modal = bootstrap.Modal.getInstance(document.getElementById('addQuestionModal'));
        modal.hide();
    });

    // Toggle "No Questions" message visibility using shared functionality
    function toggleNoQuestionsMessage() {
        const noQuestionsMessage = document.querySelector('.no-questions-message');
        noQuestionsMessage.style.display = stagedQuestions.length === 0 ? 'block' : 'none';
    }

    toggleNoQuestionsMessage();
});
