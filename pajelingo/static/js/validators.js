import { errorRequiredField, errorEmailFormat, errorNotConfirmedPassword ,errorLengthPassword, errorDigitPassword, 
    errorLetterPassword, errorSpecialCharacterPassword, errorInvalidUsername, getInput, isValidUsername, 
    hasLetter, hasDigit, hasSpecialCharacter } from "./validation.js";

export function getEmailValidators(emailField) {
    return [
        {
            validate: function() {
                return !getInput(emailField).validity.valueMissing;
            },
            errorMessage: errorRequiredField
        },
        {
            validate: function() {
                return !getInput(emailField).validity.typeMismatch;
            },
            errorMessage: errorEmailFormat
        }
    ];
}

export function getUsernameValidators(usernameField) {
    return [
        {
            validate: function() {
                return !getInput(usernameField).validity.valueMissing;
            },
            errorMessage: errorRequiredField
        },
        {
            validate: function() {
                const username = getInput(usernameField).value;
                return isValidUsername(username);
            },
            errorMessage: errorInvalidUsername
        }
    ];
}

export function getPasswordValidators(passwordField) {
    return [
        {
            validate: function() {
                return !getInput(passwordField).validity.valueMissing;
            },
            errorMessage: errorRequiredField
        },
        {
            validate: function() {
                const password = getInput(passwordField).value;
                return (password.length >= 8) && (password.length <= 30);
            },
            errorMessage: errorLengthPassword
        },
        {
            validate: function() {
                const password = getInput(passwordField).value;
                return hasDigit(password);
            },
            errorMessage: errorDigitPassword
        },
        {
            validate: function() {
                const password = getInput(passwordField).value;
                return hasLetter(password);
            },
            errorMessage: errorLetterPassword
        },
        {
            validate: function() {
                const password = getInput(passwordField).value;
                return hasSpecialCharacter(password);
            },
            errorMessage: errorSpecialCharacterPassword
        }
    ];
}

export function getConfirmPasswordValidators(passwordField, confirmPasswordField) {
    return [
        {
            validate: function() {
                return !getInput(confirmPasswordField).validity.valueMissing;
            },
            errorMessage: errorRequiredField
        },
        {
            validate: function() {
                return (getInput(passwordField).value === getInput(confirmPasswordField).value);
            },
            errorMessage: errorNotConfirmedPassword
        }
    ];
}
