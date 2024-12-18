const csrf_token = document.querySelector('[name=csrfmiddlewaretoken]').value;

function rateHandler(event) {
    const button = event.target;
    const obj_type = button.parentElement.dataset.type;
    const obj_id = button.parentElement.dataset.id;
    const action = button.classList.contains('like-btn') ? 'like' : 'dislike';

    const request = new Request(`/rate_${obj_type}/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': csrf_token, 'Content-Type': 'application/json; charset=utf-8' },
        body: JSON.stringify({ action: action, id: obj_id }),
    });

    fetch(request)
        .then((response) => {
            if (response.status === 200) {
                response.json().then((data) => {
                    button.parentElement.getElementsByClassName('rating')[0].innerText = data['new_rating'];
                });
            }
        });
}

const rate_buttons = document.querySelectorAll('.like-btn, .dislike-btn');
for (let i = 0; i < rate_buttons.length; i++) {
    rate_buttons.item(i).addEventListener('click', rateHandler);
}
