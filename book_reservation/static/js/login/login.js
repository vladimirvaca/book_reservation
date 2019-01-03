
$('#form_signin').submit(function (event) {
    event.preventDefault();
    $.ajax({
        url: $("#form_signin").attr("action"),
        type: "POST",
        data: $("#form_signin").serialize(),
        success: function (data) {
            switch (parseInt(data.status)) {
                case -1:
                    $.notify(data.message, data.type);
                    break;
                case 0:
                    $.notify(data.message, data.type);
                    break;
                case 1:
                    $.notify(data.message, data.type);
                    window.location.replace("/dashboard");
                    break;
            }
        },
        error: function () {
            $.notify('This resource is not avalaible', 'error');
        }
    });
});
