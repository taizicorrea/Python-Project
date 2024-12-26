function setClassroomId(classroomId) {
    // Check if the classroomId is being passed correctly
    if (classroomId !== undefined && classroomId !== null) {
        // Set the classroom ID in the hidden field
        document.getElementById('classroom-id').value = classroomId;
    } else {
        console.error("Classroom ID is undefined or null.");
    }
}

function confirmRemove(studentId) {
    // Show confirmation dialog
    const confirmation = confirm("Are you sure you want to remove this student from the classroom?");

    if (confirmation) {
        // If user confirms, submit the form
        document.getElementById('removeStudentForm-' + studentId).submit();
    }
}


function confirmDeleteClass() {
    // Display a confirmation dialog to the user
    const userConfirmed = confirm("Are you sure you want to delete the classroom?");

    // If the user clicked "OK", allow the form to be submitted
    if (userConfirmed) {
        return true;
    }

    // If the user clicked "Cancel", prevent the form from being submitted
    return false;
}

function confirmUnenroll() {
    // Display a confirmation dialog to the user
    const userConfirmed = confirm("Are you sure you want to unenroll?");

    // If the user clicked "OK", allow the form to be submitted
    if (userConfirmed) {
        return true;
    }

    // If the user clicked "Cancel", prevent the form from being submitted
    return false;
}


// Sidebar toggle functionality
const sidebar = document.getElementById('sidebar');
const mainContent = document.getElementById('main-content');
const menuToggle = document.getElementById('menu-toggle');

menuToggle.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
    sidebar.classList.toggle('expanded');
    mainContent.classList.toggle('collapsed');
    mainContent.classList.toggle('expanded');
});

// Initialize Bootstrap tooltips
document.addEventListener('DOMContentLoaded', () => {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(tooltipTriggerEl => {
        new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Handle tab switching
    const tabLinks = document.querySelectorAll('.profile-sidebar a[data-bs-toggle="tab"]');
    tabLinks.forEach(tabLink => {
        tabLink.addEventListener('click', event => {
            event.preventDefault();

            // Remove active class from all sidebar links
            tabLinks.forEach(link => link.classList.remove('active'));

            // Add active class to the clicked link
            tabLink.classList.add('active');

            // Switch the tab content
            const target = document.querySelector(tabLink.getAttribute('href'));
            const activeTabs = document.querySelectorAll('.tab-pane.active');
            activeTabs.forEach(tab => tab.classList.remove('active', 'show'));
            target.classList.add('active', 'show');
        });
    });
});

function openEdit(classroomId, section, className, subject, classCode, room) {
    // Set the hidden field for classroom ID and display it
    document.getElementById('modal-classroom-id').value = classroomId;
    document.getElementById('display-classroom-id').textContent = classroomId; // Display the classroom ID in the modal

    // Set the values of the form fields in the modal
    // Set the form field values
    document.getElementById('className').value = className;
    document.getElementById('room').value = room;
    document.getElementById('section').value = section;
    document.getElementById('subject').value = subject;
}

// Open classroom details
//function openClassroom(id, section, className, subject, code) {
//    // Hide classroom cards and show classroom details
//    document.getElementById('classroom-cards').style.display = 'none';
//    const classroomDetails = document.getElementById('classroom-details');
//    classroomDetails.style.display = 'block';
//
//    // Update classroom details dynamically
//    document.getElementById('class-name').textContent = `${className} (${subject})`;
//    document.getElementById('class-section').textContent = `Section: ${section}`;
//    document.getElementById('class-join-code').innerHTML = `Class Code: <b>${code}</b>`;
//    document.getElementById('classroom-id').value = id;
//
//    // Fetch enrolled students for the People tab
//    fetch(`/classroom/${id}/students`)
//        .then(response => response.json())
//        .then(data => {
//            const teacherList = document.querySelector('.teacher-list');
//            const peopleList = document.querySelector('#people .people-list');
//            peopleList.innerHTML = ''; // Clear existing content
//            teacherList.innerHTML = '';
//
//            // Display teacher information
//            if (data.teacher) {
//                const teacher = data.teacher;
//                const profile = data.current_user === 'teacher' ? '(You)' : '(Instructor)';
//                teacherList.innerHTML += `
//                    <div class="d-flex align-items-center mb-3">
//                        <img src="${teacher.profile_picture_url || defaultAvatar}" alt="${teacher.first_name} ${teacher.last_name}" class="rounded-circle" width="40">
//                        <div class="ms-2">
//                            <span>${teacher.first_name} ${teacher.last_name}</span>
//                            <strong style="color: black;">${profile}</strong>
//                        </div>
//                    </div>
//                `;
//            }
//
//            // Display students
//            if (data.students.length) {
//                data.students.forEach(student => {
//                    peopleList.innerHTML += `
//                        <div class="d-flex align-items-center mb-3">
//                            <img src="${student.profile_picture_url || defaultAvatar}" alt="${student.first_name} ${student.last_name}" class="rounded-circle" width="40">
//                            <span class="me-3">${student.first_name} ${student.last_name}</span>
//                            <div class="dropdown ms-auto">
//                                <button class="btn btn-link p-0" type="button" data-bs-toggle="dropdown" aria-expanded="false">
//                                    <i class="bi bi-three-dots-vertical"></i> <!-- Bootstrap icon for 3-dots -->
//                                </button>
//                                <ul class="dropdown-menu dropdown-menu-sm">
//                                    <li>
//                                        <a class="dropdown-item">
//                                            Remove
//                                        </a>
//                                    </li>
//                                </ul>
//                            </div>
//                        </div>
//                    `;
//                   peopleList.appendChild(studentElement);
//                });
//            } else {
//                peopleList.innerHTML = '<span class="text-muted">No students enrolled yet.</span>';
//            }
//        })
//        .catch(error => console.error('Error fetching students:', error));
//}

// Show classroom cards
function showClassroomCards() {
    document.getElementById('classroom-cards').style.display = 'flex';
    document.getElementById('classroom-details').style.display = 'none';
}


function confirmDelete() {
    var confirmation = confirm("Are you sure you want to delete your account? This action cannot be undone.");
    if (confirmation) {
        // Directly submit the form when the user confirms
        document.getElementById("deleteAccountForm").submit();
    }
}

function confirmRemove(studentId) {
    Swal.fire({
        title: 'Are you sure?',
        text: 'This will remove the student from the class.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Yes',
    }).then((result) => {
        if (result.isConfirmed) {
            document.getElementById(`removeStudentForm-${studentId}`).submit();
        }
    });
}






