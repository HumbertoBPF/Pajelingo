import { addFieldValidation, errorRequiredField, getInput } from "./validation.js";

let usernameField = document.querySelector("form .form-floating:nth-child(2)");
let passwordField = document.querySelector("form .form-floating:nth-child(3)");

const usernameValidators = [
    {
        validate: function() {
            return !getInput(usernameField).validity.valueMissing;
        },
        errorMessage: errorRequiredField
    }
]
const passwordValidators = [
    {
        validate: function() {
            return !getInput(passwordField).validity.valueMissing;
        },
        errorMessage: errorRequiredField
    }
];

addFieldValidation(usernameField, usernameValidators);
addFieldValidation(passwordField, passwordValidators);