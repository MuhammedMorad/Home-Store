 // Toggle password visibility
const togglePassword = document.getElementById("togglePassword");
const passwordField = document.getElementById("password");

togglePassword.addEventListener("click", function() {
     // Toggle the type attribute
   const type = passwordField.type === "password" ? "text" : "password";
      passwordField.type = type;
     // Toggle eye icon
      this.classList.toggle("fa-eye-slash");
});