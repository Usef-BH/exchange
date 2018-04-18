let input_base = document.querySelector('.input_base');
let input_target = document.querySelector('.input_target');
let select_base = document.querySelector('.select_base');
let select_target = document.querySelector('.select_target');
let output = document.querySelector('.output');
let output_hist = document.querySelector('.output_hist');
let output_base = document.querySelector('.output_base');
let output_symbols = document.querySelector('.output_symbols');
let base = document.querySelector('.base');
let rates = document.querySelector('.rates');

function process() {
    let base_value = select_base.value;
    let target_value = select_target.value
    let amount = input_base.value;
    fetch(`http://django-env.grpimarsjd.eu-west-3.elasticbeanstalk.com/api/?amount=${amount}&base=${base_value}&target=${target_value}`)
        .then(resp => resp.json())
        .then(data => {
            input_target.value = data.response;
        })
        .catch(err => console.error(err));
}

function grab_latest(selectorTooltip) {
    tooltipTextSend(selectorTooltip);
    fetch('http://django-env.grpimarsjd.eu-west-3.elasticbeanstalk.com/api/latest')
        .then(resp => resp.json())
        .then(data => {
            output.innerText = JSON.stringify(data, undefined, 4);
            //rates.innerText = data.price;
            output.classList.add("show");
        })
        .catch(err => console.error(err));
}

function grab_hist(selectorTooltip) {
    tooltipTextSend(selectorTooltip);
    fetch('http://django-env.grpimarsjd.eu-west-3.elasticbeanstalk.com/api/2018-03-14')
        .then(resp => resp.json())
        .then(data => {
            output_hist.innerText = JSON.stringify(data, undefined, 4);
            //rates.innerText = data.price;
            output_hist.classList.add("show");
        })
        .catch(err => console.error(err));
}

function grab_base(selectorTooltip) {
    tooltipTextSend(selectorTooltip);
    fetch('http://django-env.grpimarsjd.eu-west-3.elasticbeanstalk.com/api/latest?base=USD&symbols=EUR,GBP,JPY')
        .then(resp => resp.json())
        .then(data => {
            output_base.innerText = JSON.stringify(data, undefined, 4);
            //rates.innerText = data.price;
            output_base.classList.add("show");
        })
        .catch(err => console.error(err));
}

function grab_symbols(selectorTooltip) {
    tooltipTextSend(selectorTooltip);
    fetch('http://django-env.grpimarsjd.eu-west-3.elasticbeanstalk.com/api/latest?symbols=USD,GBP')
        .then(resp => resp.json())
        .then(data => {
            output_symbols.innerText = JSON.stringify(data, undefined, 4);
            //rates.innerText = data.price;
            output_symbols.classList.add("show");
        })
        .catch(err => console.error(err));
}

function copy(selector, selectorTooltip) {
    tooltipTextCopy(selectorTooltip);
    let ele = document.querySelector(selector);
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

document.getElementsByTagName('BODY')[0].addEventListener('copy', (e) => {
    console.log(e.target.innerText);
});

function tooltipTextSend(selector) {
    let tooltip = document.querySelector(selector);
    tooltip.innerText = "Request Sent";
}

function tooltipTextCopy(selector) {
    let tooltip = document.querySelector(selector);
    tooltip.innerText = "Copied!";
}

function resetTextCopy(ele) {
    let tooltip = document.querySelector(ele);
    tooltip.innerText = "Copy to clipboard"
}

function resetTextSend(ele) {
    let tooltip = document.querySelector(ele);
    tooltip.innerText = "Send request"
}