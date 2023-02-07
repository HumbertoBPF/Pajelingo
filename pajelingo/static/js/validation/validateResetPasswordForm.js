import { addFieldValidation } from "./validation.js";

import { getPasswordValidators, getConfirmPasswordValidators } from "./validators.js";

let passwordField = document.querySelector("form .form-floating:nth-child(2)");
let confirmPasswordField = document.querySelector("form .form-floating:nth-child(3)");

const passwordValidators = getPasswordValidators(passwordField);
const confirmPasswordValidators = getConfirmPasswordValidators(passwordField, confirmPasswordField);

addFieldValidation(passwordField, passwordValidators);
addFieldValidation(confirmPasswordField, confirmPasswordValidators);
