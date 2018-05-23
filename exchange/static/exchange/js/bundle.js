let input_base = document.querySelector('.input_base');
let input_target = document.querySelector('.input_target');
let select_base = document.querySelector('.select_base');
let select_target = document.querySelector('.select_target');
let go = document.querySelector('.go');

go.addEventListener('click', process);


function process() {
    let base_value = select_base.value;
    let target_value = select_target.value
    let amount = input_base.value;
    //console.log("Hello from javascript lando!!!!");
    //console.log('select_base:', base_value);
    //console.log('select_target:', target_value);
    if (amount == '' ) {
        return
    }
    fetch(`http://192.168.0.171:8000/api/?amount=${amount}&base=${base_value}&symbols=${target_value}`)
        .then(resp => resp.json())
        .then(data => {
            if(data.detail) {
                console.log(data);
                createModal(data.detail);
            }
            input_target.value = data.response;
        })
        .catch(err => console.error(err));
}

select_target.addEventListener('change', function(event) {
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
});

function createModal(data="Some Error Occured!") {

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
    document.querySelector('.modal').addEventListener("click", (e) => {
        e.stopPropagation();
    })
    document.body.classList.toggle("noscroll");
    document.querySelector('.overlay').addEventListener('click', remove);
    document.querySelector('.ok').addEventListener('click', remove);
}

function remove(e) {
    let overlay = document.querySelector('.overlay')
    document.body.removeChild(overlay);
    document.body.classList.toggle("noscroll");
}


//django-env.grpimarsjd.eu-west-3.elasticbeanstalk.com