function toggleEye() {
    let iconElement = document.getElementById("icon");
    let pass = document.getElementById("password")

    if (iconElement.classList.contains("fa-eye-slash")) {
      iconElement.classList.remove("fa-eye-slash");
      iconElement.classList.add("fa-eye");
      pass.type = "text";
    } else {
      iconElement.classList.remove("fa-eye");
      iconElement.classList.add("fa-eye-slash"); 
      pass.type = "password";
    }
  }