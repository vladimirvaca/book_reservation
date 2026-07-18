
var forms = document.getElementsByClassName('needs-validation');

var validation = Array.prototype.filter.call(forms, function (form) {
    form.addEventListener('submit', function (event) {
        if (form.checkValidity() === false) {
            event.preventDefault();
            event.stopPropagation();
        }
        form.classList.add('was-validated');
    }, false);
});


/* ============================================================
   Toast notifications
   ============================================================ */

var LBR_TOAST_META = {
    'success': { icon: 'fa-check-circle',       title: 'Success' },
    'error':   { icon: 'fa-exclamation-circle', title: 'Error' },
    'warning': { icon: 'fa-exclamation-triangle', title: 'Warning' },
    'warn':    { icon: 'fa-exclamation-triangle', title: 'Warning' },
    'info':    { icon: 'fa-info-circle',        title: 'Notice' }
};

function showAlert(type, message, duration) {
    if (!LBR_TOAST_META[type]) {
        type = 'info';
    }
    var meta = LBR_TOAST_META[type];
    duration = duration || (type === 'error' ? 5000 : 4000);

    var $container = $('#lbr-toast-container');
    if ($container.length === 0) {
        $container = $('<div id="lbr-toast-container" aria-live="polite"></div>').appendTo('body');
    }

    var $toast = $(
        '<div class="lbr-toast lbr-toast--' + type + '" role="alert">' +
            '<span class="lbr-toast-icon"><i class="fas ' + meta.icon + '"></i></span>' +
            '<div class="lbr-toast-body">' +
                '<p class="lbr-toast-title"></p>' +
                '<p class="lbr-toast-message"></p>' +
            '</div>' +
            '<button type="button" class="lbr-toast-close" aria-label="Close">&times;</button>' +
            '<span class="lbr-toast-progress"></span>' +
        '</div>'
    );
    $toast.find('.lbr-toast-title').text(meta.title);
    $toast.find('.lbr-toast-message').text(message);
    $toast.find('.lbr-toast-progress').css('animation-duration', duration + 'ms');

    function dismiss() {
        if ($toast.hasClass('lbr-toast--leaving')) {
            return;
        }
        $toast.addClass('lbr-toast--leaving');
        setTimeout(function () { $toast.remove(); }, 300);
    }

    $toast.find('.lbr-toast-close').on('click', dismiss);
    // Dismiss when the progress bar finishes; hovering pauses the
    // animation (see CSS), which also pauses the auto-dismiss.
    $toast.find('.lbr-toast-progress').on('animationend', dismiss);

    $container.append($toast);
    $toast[0].offsetHeight; // force reflow so the enter transition plays
    $toast.addClass('lbr-toast--visible');
}


/* ============================================================
   Button loading state
   ============================================================ */

function setButtonLoading(btn, loading) {
    var $btn = $(btn);
    if (loading) {
        if ($btn.data('lbrLoading')) {
            return;
        }
        $btn.data('lbrLoading', true);
        $btn.data('lbrOriginalHtml', $btn.html());
        $btn.css('width', $btn.outerWidth() + 'px'); // keep size while content swaps
        $btn.prop('disabled', true);
        $btn.html('<span class="lbr-spinner" role="status" aria-hidden="true"></span>');
    } else {
        if (!$btn.data('lbrLoading')) {
            return;
        }
        $btn.html($btn.data('lbrOriginalHtml'));
        $btn.css('width', '');
        $btn.prop('disabled', false);
        $btn.data('lbrLoading', false);
    }
}

/* Freeze/unfreeze a whole form while a request is in flight: disables
   every field and button (plus the modal's header close, if any) so the
   user can neither re-submit nor edit data mid-request. Only controls
   enabled at lock time are re-enabled, so it composes with
   setButtonLoading. NOTE: serialize the form BEFORE locking it —
   disabled fields are excluded from jQuery .serialize(). */
function setFormLoading(form, loading) {
    var $form = $(form);
    var $modalClose = $form.closest('.modal').find('.modal-header .close');
    if (loading) {
        if ($form.data('lbrFormLoading')) {
            return;
        }
        $form.data('lbrFormLoading', true);
        $form.addClass('lbr-form-loading');
        $form.find('input, select, textarea, button').add($modalClose)
            .not(':disabled')
            .addClass('lbr-loading-locked')
            .prop('disabled', true);
    } else {
        if (!$form.data('lbrFormLoading')) {
            return;
        }
        $form.data('lbrFormLoading', false);
        $form.removeClass('lbr-form-loading');
        $form.find('.lbr-loading-locked').add($modalClose.filter('.lbr-loading-locked'))
            .prop('disabled', false)
            .removeClass('lbr-loading-locked');
    }
}

// Shared DataTables options for the ajax loading indicator.
var LBR_DT_PROCESSING = '<div class="lbr-dt-loading"><span class="lbr-spinner"></span>&nbsp; Loading&hellip;</div>';
