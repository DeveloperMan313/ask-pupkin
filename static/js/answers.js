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

    const answerHTML =
        `
<div class="card mb-4 bg-body-tertiary" id="answer{ANSWER_ID}">
    <div class="row g-0">
        <div class="col-4 text-center" style="width: 10em;">
            <img src="{PFP_URL}" class="img-fluid rounded w-50 my-3" alt="...">
            <div class="rating-area w-50 my-3" data-type="answer" data-id="{ANSWER_ID}"
                data-user-rating="0">
                <p class="rating mb-0">0</p>
                <img src="/svg/triangle-up.svg" alt="dislike" class="dislike-btn me-2" style="transform: rotate(180deg);"><img src="/svg/triangle-up.svg" alt="like" class="like-btn">
            </div>
        </div>
        <div class="col-8">
            <div class="card-body h-100 position-relative">
                <p class="card-text pb-5">{ANSWER_TEXT}</p>
                <div class="position-absolute bottom-0 start-0 p-4">
                    <input class="correct-checkbox form-check-input mt-0" type="checkbox" value="correct" aria-label="correct answer"
                        style="vertical-align: middle;" {DISABLED} data-id="{ANSWER_ID}"><span class="ms-2" style="vertical-align: middle;">Correct</span>
                </div>
            </div>
        </div>
    </div>
</div>`;

    const answersContainer = document.getElementById('answers-container');
    const thisDataset = document.currentScript.dataset;

    const centrifuge = new Centrifuge(thisDataset.centUrl, {
        token: thisDataset.centToken
    });
    centrifuge.connect();
    const sub = centrifuge.newSubscription(String(thisDataset.questionId));

    sub.on('publication', function (ctx) {
        const data = ctx.data;
        const newAnswerHTML = answerHTML
            .replaceAll('{ANSWER_ID}', data.answer_id)
            .replaceAll('{PFP_URL}', data.pfp_url)
            .replaceAll('{ANSWER_TEXT}', data.answer_text)
            .replaceAll('{DISABLED}', (parseInt(thisDataset.ownQuestion)) ? '' : 'disabled');
        answersContainer.innerHTML += newAnswerHTML;
        const answerTagId = `answer${data.answer_id}`;
        document.getElementById(answerTagId).addEventListener('change', checkHandler);
        document.querySelector(`#${answerTagId} .like-btn`).addEventListener('click', rateHandler);
        document.querySelector(`#${answerTagId} .dislike-btn`).addEventListener('click', rateHandler);
    }).subscribe();
})();
