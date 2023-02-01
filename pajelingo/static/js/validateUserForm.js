import { addFieldValidation } from "./validation.js";

import { getEmailValidators, getUsernameValidators, getPasswordValidators, getConfirmPasswordValidators } from "./validators.js";

let emailField = document.querySelector("form .form-floating:nth-child(2)");
let usernameField = document.querySelector("form .form-floating:nth-child(3)");
let passwordField = document.querySelector("form .form-floating:nth-child(4)");
let confirmPasswordField = document.querySelector("form .form-floating:nth-child(5)");

const emailValidators = getEmailValidators(emailField);
const usernameValidators = getUsernameValidators(usernameField);
const passwordValidators = getPasswordValidators(passwordField);
const confirmPasswordValidators = getConfirmPasswordValidators(passwordField, confirmPasswordField);

addFieldValidation(emailField, emailValidators);
addFieldValidation(usernameField, usernameValidators);
addFieldValidation(passwordField, passwordValidators);
addFieldValidation(confirmPasswordField, confirmPasswordValidators);
