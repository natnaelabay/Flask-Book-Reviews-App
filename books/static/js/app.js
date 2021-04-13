/**
 * @author Natnael Abay ATR/8016/11
 * app.js
 */
const errors = document.querySelector(".errors");
const elem = document.querySelector("#sign-up");
// ! Registering

let f_name = document.querySelector("#f_name");
let l_name = document.querySelector("#l_name");
let u_name = document.querySelector("#u_name");
let password = document.querySelector("#password");
let file = document.querySelector("#profile-upload");
let password_confirm = document.querySelector("#password_confirm");
let registerForm = document.querySelector("#register-form");
let spinner_submit = document.querySelector("#r-spinner");
let r_submit = document.querySelector("#registered-submit");
// ! logging in
const loginForm = document.querySelector("#login-form");

// let registerForm = document.querySelector("#register-form")
registerForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const formData = new FormData();
  console.log(spinner_submit.classList);
  spinner_submit.classList.remove("d-none");
  r_submit.disabled = true
  if (
    f_name.value.length == 0 ||
    l_name.value.length == 0 ||
    u_name.value.length == 0 ||
    password.value.length == 0 ||
    password_confirm.value.length == 0
  ) {
    errors.innerHTML = `
        <div class="alert mx-5 h-25  alert-success" role="alert">
           Some of the Inputs are empty
        </div>
        `;
  } else {
    formData.append("f_name", f_name.value);
    formData.append("l_name", l_name.value);
    formData.append("u_name", u_name.value);
    formData.append("password", password.value);
    if (file.files.length > 0) formData.append("img", file.files[0]);

    formData.append("password_confirm", password_confirm.value);
    axios({
      method: "post",
      url: "auth/register",
      data: formData,
      headers: { "Content-Type": "multipart/form-data" },
    })
      .then((res) => {
        errors.innerHTML = "";
        r = res.data;
        if (r.success) {
          registerForm.reset();
          let message = `<div class="alert mx-5 h-25  alert-success" role="alert">
                            Successfully registered You can login now
                        </div>`;
          errors.innerHTML = message;
        } else {
          let message = "";
          for (err of r.errors) {
            message += `<div class="alert mx-5 h-25  alert-success" role="alert">
                            ${err}
                         </div>`;
          }

          errors.innerHTML = message;
        }
      })
      .catch((res) => {
        console.log("This is not it");
        console.log(res);
      });
    //   <!-- console.log(formData.getAll()) -->
  }
  r_submit.disabled = false
  spinner_submit.classList.add("d-none");

});

loginForm.addEventListener("submit", (e) => {
  e.preventDefault();

  console.log("submitted");
});
const loadFile = function (event) {
  var output = document.getElementById("profile-image");
  output.src = URL.createObjectURL(event.target.files[0]);
  output.onload = function () {
    URL.revokeObjectURL(output.src); // free memory
  };
};

/*
<script>
    const elem = document.querySelector("#sign-up")
    // const d = document.querySelector('#f_name')
    let f_name = document.querySelector("#f_name")
    let l_name = document.querySelector("#l_name")
    let u_name = document.querySelector("#u_name")
    let password = document.querySelector("#password")
    let file = document.querySelector("#profile-upload")
    let password_confirm = document.querySelector("#password_confirm")
    let registerForm = document.querySelector("#register-form")
    registerForm.addEventListener("submit", e => {
        e.preventDefault()
        const formData = new FormData()
        console.log(f_name)

        // file = file.files
        console.log(file)

        if (f_name.value.length == 0 || l_name.value.length == 0 || u_name.value.length == 0 || password.value.length == 0 || password_confirm.value.length == 0) {
            console.log("empty values present")
        } else {
            formData.append("f_name", f_name.value)
            formData.append("l_name", l_name.value)
            formData.append("u_name", u_name.value)
            formData.append("password", password.value)
            formData.append("img", file.files[0])
            formData.append("password_confirm", password_confirm.value)
            axios({
                method: "post",
                url: "auth/register",
                data: formData,
                headers: { "Content-Type": "multipart/form-data" },
            })
                .then(function (response) {
                    //handle success
                    console.log(response);
                })
                .catch(function (response) {
                    //handle error
                    console.log(response);
                });
            //   <!-- console.log(formData.getAll()) -->
        }
    })
    const loadFile = function (event) {
        var output = document.getElementById('profile-image');
        output.src = URL.createObjectURL(event.target.files[0]);
        output.onload = function () {
            URL.revokeObjectURL(output.src) // free memory
        }
    };
    elem.addEventListener("click", e => {
        d.focus()
    })
        // this is to click the button
        // document.querySelectorAll(".nav-link")[1].click()
</script>
*/
