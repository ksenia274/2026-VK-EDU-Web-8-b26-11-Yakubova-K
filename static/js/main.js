$(function () {
    function getCsrfToken() {
        const match = document.cookie.match(/csrftoken=([^;]+)/);
        return match ? match[1] : '';
    }

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!this.crossDomain) {
                xhr.setRequestHeader('X-CSRFToken', getCsrfToken());
            }
        },
    });

    $(document).on('click', '.vote-btn', function () {
        const btn = $(this);
        const contentType = btn.data('content-type');
        const id = btn.data('id');
        const value = btn.data('value');

        const url = (typeof URLS !== 'undefined')
            ? (contentType === 'question' ? URLS.likeQuestion : URLS.likeAnswer)
            : (contentType === 'question' ? '/like/question/' : '/like/answer/');

        $.post(url, { id: id, value: value })
            .done(function (data) {
                if (contentType === 'question') {
                    $('#question-rating').text(data.rating);
                } else {
                    $('#answer-rating-' + id).text(data.rating);
                }

                const likeBtn    = $('[data-content-type="' + contentType + '"][data-id="' + id + '"][data-value="like"]');
                const dislikeBtn = $('[data-content-type="' + contentType + '"][data-id="' + id + '"][data-value="dislike"]');

                likeBtn.removeClass('btn-primary btn-outline-secondary')
                       .addClass(data.user_vote === 1 ? 'btn-primary' : 'btn-outline-secondary');
                dislikeBtn.removeClass('btn-danger btn-outline-secondary')
                          .addClass(data.user_vote === -1 ? 'btn-danger' : 'btn-outline-secondary');
            })
            .fail(function (xhr) {
                handleAjaxError(xhr);
            });
    });

    $(document).on('click', '.mark-correct-btn', function () {
        const btn        = $(this);
        const questionId = btn.data('question-id');
        const answerId   = btn.data('answer-id');

        const url = (typeof URLS !== 'undefined') ? URLS.markCorrect : '/mark-correct/';

        $.post(url, { question_id: questionId, answer_id: answerId })
            .done(function (data) {
                $('.card[id^="answer-"]').removeClass('border-success');
                $('.correct-badge').addClass('d-none');
                $('.mark-correct-btn')
                    .removeClass('btn-success').addClass('btn-outline-success')
                    .text('Отметить');

                if (data.is_correct) {
                    const card = $('#answer-' + data.answer_id);
                    card.addClass('border-success');
                    card.find('.correct-badge').removeClass('d-none');
                    btn.removeClass('btn-outline-success').addClass('btn-success');
                }
            })
            .fail(function (xhr) {
                handleAjaxError(xhr);
            });
    });

    function handleAjaxError(xhr) {
        const data = xhr.responseJSON || {};
        if (xhr.status === 401) {
            const loginUrl = data.login_url || (typeof URLS !== 'undefined' ? URLS.loginUrl : '/login/');
            window.location.href = loginUrl + '?next=' + encodeURIComponent(window.location.pathname);
        } else if (xhr.status === 403) {
            alert('Доступ запрещён: ' + (data.error || 'недостаточно прав.'));
        } else if (xhr.status === 404) {
            alert('Объект не найден.');
        } else if (xhr.status === 400) {
            const errors = data.errors || {};
            const messages = Object.values(errors).flat().join('\n');
            alert('Ошибка валидации:\n' + (messages || JSON.stringify(data)));
        } else if (xhr.status === 405) {
            alert('Метод не разрешён. Используйте POST.');
        } else {
            alert('Произошла ошибка (' + xhr.status + '). Попробуйте ещё раз.');
        }
    }
});
