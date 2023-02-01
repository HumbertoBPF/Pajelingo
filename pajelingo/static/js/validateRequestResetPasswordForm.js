import { addFieldValidation } from "./validation.js";

import { getEmailValidators } from "./validators.js";

let emailField = document.querySelector("form .form-floating:nth-child(2)");
const emailValidators = getEmailValidators(emailField);

addFieldValidation(emailField, emailValidators);