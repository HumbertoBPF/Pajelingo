export const errorRequiredField = "This field is required.";
export const errorEmailFormat = "Enter a valid email address.";
export const errorNotConfirmedPassword = "The passwords do not match.";
export const errorLetterPassword = "The password must have at least one letter.";
export const errorDigitPassword = "The password must have at least one digit.";
export const errorSpecialCharacterPassword = "The password must have at least one special character.";
export const errorLengthPassword = "The password must have a length between 8 and 30.";
export const errorInvalidUsername = "Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_ characters.";
export const errorImageFileFormat = "Upload a valid image. The file you uploaded was either not an image or a corrupted image."
export const errorTooShortUsername = "The username must be at least 8 characters-long.";

export function addFieldValidation(field, validators) {
    field.querySelector(".form-control").addEventListener("focus", function() {
        validateField(field, validators);
    });
    field.querySelector(".form-control").addEventListener("input", function() {
        validateField(field, validators);
    });
}

export function validateField(field, validators) {
    let input = field.querySelector(".form-control");
    let error = field.querySelector(".invalid-feedback");

    resetErrors(input, error);

    let errorList = "<ul>";

    validators.forEach(validator => {
        if (!validator.validate()) {
            errorList += `<li>${validator.errorMessage}</li>`; 
        }
    });

    errorList += "</ul>";

    if (errorList != "<ul></ul>") {
        setErrors(input, error, errorList)
    }
}

function resetErrors(input, error){
    input.classList.remove("is-invalid");
    error.innerHTML = "";
}

function setErrors(input, error, errorMessage){
    input.classList.add("is-invalid");
    error.innerHTML = errorMessage;
}

export function getInput(field) {
    return field.querySelector(".form-control");
}

export function searchPattern(pattern, text) {
    return pattern.test(text);
}

export function isValidUsername(text) {
    return !searchPattern(/[^@.+-_0-9A-Za-z]/, text);
}

export function hasLetter(text) {
    return searchPattern(/[A-Z]/, text) || searchPattern(/[a-z]/, text);
}

export function hasDigit(text){
    return searchPattern(/[0-9]/, text);
}

export function hasSpecialCharacter(text){
    return searchPattern(/[!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~]/, text);
}