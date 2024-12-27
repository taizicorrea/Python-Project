document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("search-students");
    const suggestionsContainer = document.getElementById("student-suggestions");
    const selectedStudentsList = document.getElementById("selected-students");
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    let selectedStudents = new Set();

    // Function to fetch student suggestions from the server
    searchInput.addEventListener("input", function () {
        const query = searchInput.value.trim();

        if (query.length < 2) {
            suggestionsContainer.style.display = "none";
            return;
        }

        fetch(`/search_students/?q=${encodeURIComponent(query)}`)
            .then((response) => {
                if (!response.ok) throw new Error("Failed to fetch suggestions");
                return response.json();
            })
            .then((data) => {
                suggestionsContainer.innerHTML = "";
                if (data.students.length === 0) {
                    const noResult = document.createElement("div");
                    noResult.className = "dropdown-item text-muted";
                    noResult.textContent = "No students found";
                    suggestionsContainer.appendChild(noResult);
                    suggestionsContainer.style.display = "block";
                    return;
                }

                suggestionsContainer.style.display = "block";
                data.students.forEach((student) => {
                    const item = document.createElement("button");
                    item.type = "button";
                    item.className = "dropdown-item";
                    item.textContent = `${student.first_name} ${student.last_name} (${student.email})`;
                    item.dataset.id = student.id;

                    item.addEventListener("click", function () {
                        addStudentToList(student);
                        suggestionsContainer.style.display = "none";
                        searchInput.value = "";
                    });

                    suggestionsContainer.appendChild(item);
                });
            })
            .catch((error) => {
                console.error("Error fetching suggestions:", error);
                const errorItem = document.createElement("div");
                errorItem.className = "dropdown-item text-danger";
                errorItem.textContent = "Error loading suggestions";
                suggestionsContainer.innerHTML = "";
                suggestionsContainer.appendChild(errorItem);
                suggestionsContainer.style.display = "block";
            });
    });

    // Function to add selected student to the list
    function addStudentToList(student) {
        if (selectedStudents.has(student.id)) return;

        selectedStudents.add(student.id);

        const li = document.createElement("li");
        li.className = "list-group-item d-flex justify-content-between align-items-center";
        li.textContent = `${student.first_name} ${student.last_name} (${student.email})`;

        const removeButton = document.createElement("button");
        removeButton.type = "button";
        removeButton.className = "btn btn-sm btn-danger ms-2";
        removeButton.textContent = "Remove";

        removeButton.addEventListener("click", function () {
            selectedStudents.delete(student.id);
            li.remove();
        });

        li.appendChild(removeButton);
        selectedStudentsList.appendChild(li);

        // Add a hidden input to the form for each selected student
        const hiddenInput = document.createElement("input");
        hiddenInput.type = "hidden";
        hiddenInput.name = "student_ids[]";
        hiddenInput.value = student.id;
        li.appendChild(hiddenInput);
    }

    // Hide suggestions when clicking outside
    document.addEventListener("click", function (e) {
        if (!searchInput.contains(e.target) && !suggestionsContainer.contains(e.target)) {
            suggestionsContainer.style.display = "none";
        }
    });

    // Function to send selected students to the server
    document.getElementById("add-students-button").addEventListener("click", function (event) {
        event.preventDefault(); // Prevent default form submission

        const classroomId = document.getElementById("classroom-id").value;
        const studentIds = Array.from(selectedStudents);

        if (!classroomId || studentIds.length === 0) {
            Swal.fire({
                icon: 'warning',
                title: 'Oops...',
                text: 'Please select at least one student and ensure the classroom ID is set.'
            });
            return;
        }

        fetch('/add_students/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                classroom_id: classroomId,
                student_ids: studentIds,
            }),
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Failed to add students.');
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                Swal.fire({
                    icon: 'success',
                    title: 'Students Added',
                    text: `Students added successfully: ${data.added_students.join(', ')}`,
                }).then(() => {
                    // Reload the page after the alert is dismissed
                    location.reload();
                });
                selectedStudents.clear();
                selectedStudentsList.innerHTML = "";
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: data.error || 'Unknown error.',
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: `An error occurred: ${error.message}`,
            });
        });
    });
});
