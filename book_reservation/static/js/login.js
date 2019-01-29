
$('#form_signin').submit(function (event) {
    event.preventDefault();
    $.ajax({
        url: $("#form_signin").attr("action"),
        type: "POST",
        data: $("#form_signin").serialize(),
        success: function (data) {
            switch (parseInt(data.status)) {
                case -1:
                    showAlert(data.type, data.message);
                    break;
                case 0:
                    showAlert(data.type, data.message);
                    break;
                case 1:
                    showAlert(data.type, data.message);
                    window.location.replace("/dashboard");
                    break;
            }
        },
        error: function () {
            $.notify('This resource is not avalaible', 'error');
        }
    });
});

