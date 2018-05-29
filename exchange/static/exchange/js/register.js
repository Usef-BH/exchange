let token_input = document.getElementsByName('csrfmiddlewaretoken')[0];
let email_input = document.getElementById('email');
let password_input = document.getElementById('password');
let submit_button = document.querySelector('.submit');

submit_button.addEventListener('click', submit)

function submit() {
    document.activeElement.blur();
    let email = email_input.value;

    let is_valid = validate_email(email);
    if (is_valid) {
        let password = password_input.value;
        console.log(`email ${email} is valid`);
        let csrfmiddlewaretoken = token_input.value;
        let data = { email, password }

        fetch("http://192.168.0.171:8000/register/", {
            method: 'POST',
            credentials: "include",
            headers: {
                "X-CSRFToken": csrfmiddlewaretoken,
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data),
        })
        .then(resp => resp.json())
        .then(data => {
            if(data.success) {
                createSuccessModal(data.token);
            } else {
                createInfoModal(data.token);
            }
            email_input.value = '';
            password_input.value = '';
        })
        .catch(console.error);
    }
    else {
        console.log(`${email} NOT A VALID EMAIL!`);
        createErrorModal(`${email} NOT A VALID EMAIL!`);

    }
}

function validate_email(email) {
    let regex = /^[a-zA-Z][a-zA-Z0-9]*@[a-zA-Z]*\.[a-zA-Z]{2,8}/;
    return regex.test(email);
}

function createInfoModal(data) {
    let template = `<div class="overlay" tabindex="-1">
    <div class="modal modal-success" role="dialog" aria-modal="true">   
        <div class="swal-icon swal-icon--info"></div>      
        <div class="token">
            <button class="btn_copy tooltip koko" role="Copy to clipboard">
                <img src="http://192.168.0.171:8000/static/exchange/img/clippy.svg" 
                width="17px" alt="Copy to clipboard">
                <span class="tooltiptext tooltiptext_latest_copy">Copy to clipboard</span>
            </button>
            <div class="api_request hey">
                <pre class="output_data">${data}</pre>
            </div>
        </div>
        <span class="greetings">
            You Already registered! This is your token. <br/> 
            See how to use this API 
            <a href="/docs" style="color: red;">here</a>
        </span>
        <button class="ok success">OK</button>
    </div>
    </div>`

    document.body.insertAdjacentHTML('beforeend', template);
    handleEvants();
}

function createErrorModal(data) {
    let template = `<div class="overlay" tabindex="-1">
        <div class="modal" role="dialog" aria-modal="true">           
            <div class="swal-icon swal-icon--error">
                <div class="swal-icon--error__x-mark">
                <span class="swal-icon--error__line swal-icon--error__line--left"></span>
                <span class="swal-icon--error__line swal-icon--error__line--right"></span>
                </div>
            </div>
            <span class="greetings">
                ${data}
            </span>
            <button class="ok error">OK</button>
        </div>
    </div>`

    document.body.insertAdjacentHTML('beforeend', template);
    handleEvants(true);
}

function createSuccessModal(data) {
    let template = `<div class="overlay" tabindex="-1">
    <div class="modal modal-success" role="dialog" aria-modal="true">   
        <div class="swal-icon swal-icon--success">
            <span class="swal-icon--success__line swal-icon--success__line--long"></span>
            <span class="swal-icon--success__line swal-icon--success__line--tip"></span>
            <div class="swal-icon--success__ring"></div>
            <div class="swal-icon--success__hide-corners"></div>
        </div>        
        <div class="token">
            <button class="btn_copy tooltip koko" role="Copy to clipboard">
                <img src="http://192.168.0.171:8000/static/exchange/img/clippy.svg" 
                width="17px" alt="Copy to clipboard">
                <span class="tooltiptext tooltiptext_latest_copy">Copy to clipboard</span>
            </button>
            <div class="api_request hey">
                <pre class="output_data">${data}</pre>
            </div>
        </div>
        <span class="greetings">
            Thank you for joining us.<br/> Take note of your token, and 
            See how to use this API 
            <a href="/docs" style="color: red;">here</a>
        </span>
        <button class="ok success">OK</button>
    </div>
    </div>`;

    document.body.insertAdjacentHTML('beforeend', template);
    handleEvants();

}

function handleEvants(error=false) {
    document.querySelector('.modal').addEventListener("click", (e) => {
        e.stopPropagation();
    })
    document.body.classList.toggle("noscroll");
    document.querySelector('.overlay').addEventListener('click', remove);
    document.querySelector('.ok').addEventListener('click', remove);
    if (!error) {
        document.querySelector('.btn_copy').addEventListener('click', copy);
        document.querySelector('.btn_copy').addEventListener('mouseout', resetTextCopy);
    }
}

function remove(e) {
    let overlay = document.querySelector('.overlay')
    document.body.removeChild(overlay);
    document.body.classList.toggle("noscroll");
}

function tooltipTextCopy() {
    let tooltip = document.querySelector('.tooltiptext_latest_copy');
    tooltip.innerText = "Copied!";
}

function copy() {
    let selectorTooltip = document.querySelector('.tooltiptext_latest_copy');
    tooltipTextCopy();
    let ele = document.querySelector('.output_data');
    var range = document.createRange();
    var selection = window.getSelection();
    range.selectNodeContents(ele);
    selection.removeAllRanges();
    selection.addRange(range);
    try {
        document.execCommand('copy');
    }
    catch (err) {
        console.log(err);
    }
    selection.removeAllRanges();
}

function resetTextCopy() {
    let selectorTooltip = document.querySelector('.tooltiptext_latest_copy');
    selectorTooltip.innerText = "Copy to clipboard"
}
