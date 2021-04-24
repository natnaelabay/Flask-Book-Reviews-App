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
let log_username = document.querySelector("#login-username");
let log_password = document.querySelector("#login-password");
let login_error = document.querySelector(".login-error");

const loadFile = function (event) {
  // var output = document.getElementById("profile-upload");
  // output.src = URL.createObjectURL(event.target.files[0]);
  // output.onload = function () {
  //   URL.revokeObjectURL(output.src); // free memory
  // };
};
