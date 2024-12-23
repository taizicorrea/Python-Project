document.addEventListener('DOMContentLoaded', () => {
    const questionTypeField = document.getElementById('question_type');
    const dynamicFields = document.getElementById('dynamicFields');
    const questionForm = document.getElementById('questionForm');
    const questionModalLabel = document.getElementById('questionModalLabel');
    const questionIdField = document.getElementById('questionId');
    const saveQuestionBtn = document.getElementById('saveQuestionBtn');

    // Initialize dynamic fields on question type change
    questionTypeField.addEventListener('change', () => renderDynamicFields(questionTypeField.value));

    // Render dynamic fields based on the question type
    function renderDynamicFields(type) {
        dynamicFields.innerHTML = '';

        if (type === 'multiple_choice') {
            dynamicFields.innerHTML = `
                <div class="mb-3">
                    <label for="optionsContainer" class="form-label">Options</label>
                    <div id="optionsContainer"></div>
                    <button type="button" id="addOptionBtn" class="btn btn-sm btn-secondary mt-2">Add Option</button>
                </div>
                <div class="mb-3">
                    <label for="correct_answers" class="form-label">Correct Answer</label>
                    <input id="correct_answers" name="correct_answers" class="form-control" placeholder="Enter the correct answer(s)">
                </div>`;
            setupAddOption();
        } else if (type === 'true_false') {
            dynamicFields.innerHTML = `
                <div class="mb-3">
                    <label for="correct_answers" class="form-label">Correct Answer</label>
                    <select id="correct_answers" name="correct_answers" class="form-select">
                        <option value="True">True</option>
                        <option value="False">False</option>
                    </select>
                </div>`;
        } else if (type === 'identification') {
            dynamicFields.innerHTML = `
                <div class="mb-3">
                    <label for="answersContainer" class="form-label">Correct Answers</label>
                    <div id="answersContainer"></div>
                    <button type="button" id="addAnswerBtn" class="btn btn-sm btn-secondary mt-2">Add Answer</button>
                </div>`;
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
                <button type="button" class="btn btn-danger btn-sm removeOption">Remove</button>`;
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
                <button type="button" class="btn btn-danger btn-sm removeAnswer">Remove</button>`;
            answerWrapper.querySelector('.removeAnswer').addEventListener('click', () => answerWrapper.remove());
            answersContainer.appendChild(answerWrapper);
        });
    }

    // Handle Add Question button click
    document.getElementById('openAddQuestionModal').addEventListener('click', () => {
        questionModalLabel.textContent = 'Add Question';
        questionForm.reset();
        questionIdField.value = '';
        renderDynamicFields('multiple_choice'); // Default type
    });

    // Handle Edit Question button click
    document.querySelectorAll('.edit-question-btn').forEach(button => {
        button.addEventListener('click', (event) => {
            const buttonData = event.currentTarget.dataset;
            questionModalLabel.textContent = 'Edit Question';
            questionForm.reset();

            document.getElementById('questionId').value = buttonData.id;
            document.getElementById('question_text').value = buttonData.question;
            document.getElementById('question_type').value = buttonData.type;
            renderDynamicFields(buttonData.type);

            if (buttonData.type === 'multiple_choice') {
                const optionsContainer = document.getElementById('optionsContainer');
                const options = buttonData.options.split('\\n');
                options.forEach(option => {
                    const optionWrapper = document.createElement('div');
                    optionWrapper.classList.add('d-flex', 'mb-2');
                    optionWrapper.innerHTML = `
                        <input type="text" class="form-control me-2 option-input" value="${option}" placeholder="Enter option">
                        <button type="button" class="btn btn-danger btn-sm removeOption">Remove</button>`;
                    optionWrapper.querySelector('.removeOption').addEventListener('click', () => optionWrapper.remove());
                    optionsContainer.appendChild(optionWrapper);
                });
                document.getElementById('correct_answers').value = buttonData.answers;
            } else if (buttonData.type === 'identification') {
                const answersContainer = document.getElementById('answersContainer');
                const answers = buttonData.answers.split('\\n');
                answers.forEach(answer => {
                    const answerWrapper = document.createElement('div');
                    answerWrapper.classList.add('d-flex', 'mb-2');
                    answerWrapper.innerHTML = `
                        <input type="text" class="form-control me-2 answer-input" value="${answer}" placeholder="Enter answer">
                        <button type="button" class="btn btn-danger btn-sm removeAnswer">Remove</button>`;
                    answerWrapper.querySelector('.removeAnswer').addEventListener('click', () => answerWrapper.remove());
                    answersContainer.appendChild(answerWrapper);
                });
            } else if (buttonData.type === 'true_false') {
                document.getElementById('correct_answers').value = buttonData.answers;
            }
        });
    });

    // Save Question functionality
    saveQuestionBtn.addEventListener('click', () => {
    const questionId = questionIdField.value;
    const quizId = document.getElementById('quiz-container').dataset.quizId;
    const questionText = document.getElementById('question_text').value.trim();
    const questionType = questionTypeField.value;
    const correctAnswers = document.getElementById('correct_answers')?.value.trim() || '';
    let options = [];

    if (questionType === 'multiple_choice') {
        options = Array.from(document.querySelectorAll('.option-input'))
            .map(input => input.value.trim())
            .filter(value => value !== '');
    }

    // Validation
    if (!questionText || (questionType === 'multiple_choice' && options.length === 0)) {
        alert('Please fill out all required fields.');
        return;
    }

    const data = {
        questionId: questionId || null,
        quizId: quizId,
        question_text: questionText,
        question_type: questionType,
        options: options,
        correct_answers: correctAnswers,
    };

    console.log('Data being sent:', data); // Debug log

    // Send data to the backend
    fetch('/save_question/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        },
        body: JSON.stringify(data),
    })
        .then(response => response.json())
        .then(responseData => {
            console.log('Backend Response:', responseData); // Log response
            if (responseData.success) {
                alert('Question saved successfully!');
                location.reload(); // Reload to update the questions
            } else {
                alert(`Failed to save the question: ${responseData.error}`);
            }
        })
        .catch(error => {
            console.error('Error saving question:', error);
            alert('An error occurred while saving the question.');
        });
});


    // Render default fields for the initial state
    renderDynamicFields('multiple_choice');
});
