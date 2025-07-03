let currentRole = 'student';
let isLogin = false;

function switchRole(role, button) {
  currentRole = role;
  
  const tabs = document.querySelectorAll('.nav-tab');
  tabs.forEach(tab => tab.classList.remove('active'));
  button.classList.add('active');

  const slider = document.getElementById('nav-indicator');
  slider.style.width = `${button.offsetWidth}px`;
  slider.style.left = `${button.offsetLeft}px`;

  document.getElementById('signup-form').reset();
  document.getElementById('login-form').reset();

  // Hide all teacher notes initially
  document.getElementById('teacher-note-signup').classList.add('hidden');
  document.getElementById('teacher-note-login').classList.add('hidden');
  // Teacher Login only
  if (role === 'teacher') {
    isLogin = true;
    document.getElementById('signup-form').style.display = 'none';
    document.getElementById('login-form').style.display = 'block';
    document.getElementById('form-toggle-text').style.display = 'none';
    document.getElementById('teacher-note-login').classList.remove('hidden');
  } else {
    isLogin = false;
    document.getElementById('signup-form').style.display = 'block';
    document.getElementById('login-form').style.display = 'none';
    document.getElementById('form-toggle-text').style.display = 'block';
  }

  updateFormHeader();
}

function toggleForm() {
  isLogin = !isLogin;

  document.getElementById('signup-form').style.display = isLogin ? 'none' : 'block';
  document.getElementById('login-form').style.display = isLogin ? 'block' : 'none';

  // Hide  notes 
  document.getElementById('teacher-note-signup').classList.add('hidden');
  document.getElementById('teacher-note-login').classList.add('hidden');

  
  if (currentRole === 'teacher') {
    if (isLogin) {
      document.getElementById('teacher-note-login').classList.remove('hidden');
    } else {
      document.getElementById('teacher-note-signup').classList.remove('hidden');
    }
  }

  updateFormHeader();
}

function updateFormHeader() {
  const title = document.getElementById('form-title');
  const toggleText = document.getElementById('form-toggle-text');

  if (currentRole === 'teacher') {
    title.innerText = 'Login';
    toggleText.style.display = 'none';
  } else if (isLogin) {
    title.innerText = 'Login';
    toggleText.innerHTML = `Don't have an account? <a href="#" onclick="toggleForm()">Sign Up</a>`;
    toggleText.style.display = 'block';
  } else {
    title.innerText = 'Sign Up';
    toggleText.innerHTML = `Already have an account? <a href="#" onclick="toggleForm()">Login</a>`;
    toggleText.style.display = 'block';
  }
}
// Initialize slider on page load
window.addEventListener('DOMContentLoaded', () => {
  const active = document.querySelector('.nav-tab.active');
  const slider = document.getElementById('nav-indicator');
  slider.style.width = `${active.offsetWidth}px`;
  slider.style.left = `${active.offsetLeft}px`;
});
