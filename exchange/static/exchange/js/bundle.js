let input_base = document.querySelector('.input_base');
let input_target = document.querySelector('.input_target');
let select_base = document.querySelector('.select_base');
let select_target = document.querySelector('.select_target');
let output = document.querySelector('.output');
let base = document.querySelector('.base');
let rates = document.querySelector('.rates');

function process() {
    let base_value = select_base.value;
    let target_value = select_target.value
    let amount = input_base.value;
    console.log("Hello from javascript lando!!!!");
    console.log('select_base:', base_value);
    console.log('select_target:', target_value);
    fetch(`http://192.168.0.171:8000/api/?amount=${amount}&base=${base_value}&target=${target_value}`)
    .then(resp => resp.json())
    .then(data => {
        console.log(data);
        input_target.value = data.response;
    })
    .catch(err => console.error(err));
}

select_target.addEventListener('change', validate);

function validate() {
    let select = event.target;
    event.stopPropagation();
    console.log('hello: ', select.selectedOptions[0].value);
    if(input_base.value != '' && parseInt(input_base.value) != 0 && parseInt(input_base.value).toString() != "NaN") {
        process();
    }
    else {
        console.log(input_base.value);
        input_base.value = "";
        input_target.value = "";
    }
}

function grap_latest() {
    fetch(`http://192.168.0.171:8000/api/latest`)
    .then(resp => resp.json())
    .then(data => {
        console.log(data);
        output.innerText = JSON.stringify(data, undefined, 4);
        //rates.innerText = data.price;
        output.classList.add("show");
    })
    .catch(err => console.error(err));
}