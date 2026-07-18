
$('#form_signin').submit(function (event) {
    event.preventDefault();
    var $form = $(this);
    var formData = $form.serialize(); // before locking: disabled fields don't serialize
    var $submitBtn = $form.find('button[type="submit"]');
    var $demoBtn = $('#demo_signin_btn');

    function unlock() {
        setFormLoading($form, false);
        setButtonLoading($submitBtn, false);
        // The demo button lives outside the form, so restore it explicitly
        setButtonLoading($demoBtn, false);
        $demoBtn.prop('disabled', false);
    }

    setButtonLoading($submitBtn, true);
    setFormLoading($form, true);
    $demoBtn.prop('disabled', true);
    $.ajax({
        url: $form.attr("action"),
        type: "POST",
        data: formData,
        success: function (data) {
            switch (parseInt(data.status)) {
                case -1:
                case 0:
                    unlock();
                    showAlert(data.type, data.message);
                    break;
                case 1:
                    // Keep the form locked while the redirect happens
                    showAlert(data.type, data.message);
                    window.location.replace("/dashboard");
                    break;
            }
        },
        error: function () {
            unlock();
            showAlert('error', 'This resource is not available.');
        }
    });
});

// Demo access: fill the credentials and submit through the normal flow
$('#demo_signin_btn').on('click', function () {
    var $btn = $(this);
    $('#id_username').val($btn.data('username'));
    $('#id_password').val($btn.data('password'));
    setButtonLoading($btn, true);
    $('#form_signin').submit();
});
