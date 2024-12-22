(() => {
    const csrf_token = document.querySelector('[name=csrfmiddlewaretoken]').value;

    function checkHandler(event) {
        const checkbox = event.target;
        const user_id = checkbox.dataset.id;

        const request = new Request('/answer_correct_set/', {
            method: 'POST',
            headers: { 'X-CSRFToken': csrf_token, 'Content-Type': 'application/json; charset=utf-8' },
            body: JSON.stringify({ checked: checkbox.checked, id: user_id }),
        });

        fetch(request)
            .then((response) => {
                if (response.status !== 200) {
                    checkbox.checked = !checkbox.checked;
                }
            });
    }

    const correct_checkboxes = document.querySelectorAll('.correct-checkbox');
    for (let i = 0; i < correct_checkboxes.length; i++) {
        correct_checkboxes.item(i).addEventListener('change', checkHandler);
    }
})();
