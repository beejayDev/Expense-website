const usernameField = document.querySelector('#usernameField');
const feedbackField = document.querySelector('.invalid-feedback');
const emailField = document.querySelector('#emailField');
const emailfeedback = document.querySelector('.invalid-emailfeedback');
const usernameSuccessOutput = document.querySelector('.usernameSuccessOutput');
const emailSuccessOutput = document.querySelector('.emailSuccessOutput');
const passwordField = document.querySelector('#passwordField');
const showPasswordToggle = document.querySelector('.showPasswordToggle');
const submitBtn = document.querySelector('.submit-btn');

const handleToggleInput = (e) => {
	if(showPasswordToggle.textContent === 'SHOW') {
		showPasswordToggle.textContent = 'HIDE'
		passwordField.setAttribute('type', 'text');
	} else {
		showPasswordToggle.textContent = 'SHOW'
		passwordField.setAttribute('type', 'Password');
	}
};

showPasswordToggle.addEventListener('click', handleToggleInput);

usernameField.addEventListener('keyup', (e) => {
	let usernameVal = e.target.value;
	usernameSuccessOutput.style.display = 'block';
	usernameSuccessOutput.textContent = `Checking ${usernameVal}`;

	usernameField.classList.remove('is-invalid');
	feedbackField.style.display = 'none';

	if(usernameVal.length > 0) {
		fetch('validate-username', {
			body: JSON.stringify({ 'username': usernameVal }), 
			method: 'POST'
		})
		.then((res) => res.json())
		.then((data) => {
			usernameSuccessOutput.style.display = 'none'
			if(data.username_errors) {
				submitBtn.disabled = true;
				usernameField.classList.add('is-invalid');
				feedbackField.style.display = 'block';
				feedbackField.innerHTML = `<p>${data.username_errors}</p>`
			} else {
				submitBtn.disabled = false;
			}
		});
	}
});


emailField.addEventListener('keyup', (e) => {
	let emailVal = e.target.value;

	emailSuccessOutput.style.display = 'block'; 
	emailSuccessOutput.textContent = `Checking ${emailVal}`;

	emailField.classList.remove('is-invalid');
	emailfeedback.style.display = 'none';

	if(emailVal.length > 0) {
		fetch('validate-email', {
			body: JSON.stringify({ 'email': emailVal }),
			method: 'POST'
		})
		.then((res) => res.json())
		.then((data) => {
			emailSuccessOutput.style.display = 'none'
			if(data.email_errors) {
				submitBtn.disabled = true;
				emailField.classList.add('is-invalid');
				emailfeedback.style.display = 'block';
				emailfeedback.innerHTML = `<p>${data.email_errors}</p>`
			} else { 
				submitBtn.disabled = false;
			}
		});
	}
});

