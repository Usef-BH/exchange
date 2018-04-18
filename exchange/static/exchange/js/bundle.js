let input_base = document.querySelector('.input_base');
let input_target = document.querySelector('.input_target');
let select_base = document.querySelector('.select_base');
let select_target = document.querySelector('.select_target');


function process() {
    let base_value = select_base.value;
    let target_value = select_target.value
    let amount = input_base.value;
    //console.log("Hello from javascript lando!!!!");
    //console.log('select_base:', base_value);
    //console.log('select_target:', target_value);
    fetch(`http://django-env.grpimarsjd.eu-west-3.elasticbeanstalk.com/api/?amount=${amount}&base=${base_value}&target=${target_value}`)
        .then(resp => resp.json())
        .then(data => {
            //console.log(data);
            input_target.value = data.response;
        })
        .catch(err => console.error(err));
}

select_target.addEventListener('change', validate);

function validate() {
    let select = event.target;
    event.stopPropagation();
    //console.log('hello: ', select.selectedOptions[0].value);
    if (input_base.value != '' && parseInt(input_base.value) != 0 && parseInt(input_base.value).toString() != "NaN") {
        process();
    }
    else {
        //console.log(input_base.value);
        input_base.value = "";
        input_target.value = "";
    }
}