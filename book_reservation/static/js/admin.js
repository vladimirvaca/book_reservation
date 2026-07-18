
var adminTable = $('#admin_table').DataTable({
    'ajax': '/admins/get/',
    'responsive': true,
    'processing': true,
    'language': { 'processing': LBR_DT_PROCESSING },
    'columns': [
        { 'data': 'username' },
        {
            'data': 'email',
            'render': function (data) { return data || '—'; }
        },
        {
            'data': 'is_superuser',
            'render': function (data) { return renderRoleBadge(data); }
        },
        { 'data': 'last_login' },
        {
            'data': null,
            'orderable': false,
            'width': '5%',
            'render': function (data, type, row) {
                if (row.is_superuser) {
                    return '';
                }
                return '<button id="edit_admin_btn" class="btn btn-secondary btn-sm lbr-action-btn"><i class="far fa-edit"></i></button>';
            }
        },
        {
            'data': null,
            'orderable': false,
            'width': '5%',
            'render': function (data, type, row) {
                if (row.is_superuser) {
                    return '';
                }
                return '<button id="remove_admin_btn" class="btn btn-danger btn-sm lbr-action-btn"><i class="fas fa-trash-alt"></i></button>';
            }
        }
    ]
});

function renderRoleBadge(isSuper) {
    return isSuper
        ? '<span class="lbr-status-badge lbr-role-super">Super Admin</span>'
        : '<span class="lbr-status-badge lbr-role-admin">Admin</span>';
}

$('#form_admin').submit(function (event) {
    event.preventDefault();
    var $form = $(this);

    if (this.checkValidity() === false) {
        return;
    }
    var password1 = $('#admin_label_password1').val();
    var password2 = $('#admin_label_password2').val();
    if ((password1 || password2) && password1 !== password2) {
        showAlert('warning', 'Passwords do not match.');
        return;
    }

    var formData = $form.serialize(); // before locking: disabled fields don't serialize
    var $submitBtn = $('#admin_button_form');
    setButtonLoading($submitBtn, true);
    setFormLoading($form, true);
    $.ajax({
        url: getUrlDispatch(),
        type: 'POST',
        data: formData,
        success: function (data) {
            switch (parseInt(data.status)) {
                case -1:
                    showAlert(data.type, data.message);
                    break;
                case 1:
                    $('#admin_modal').modal('hide');
                    adminTable.ajax.reload(null, false);
                    showAlert(data.type, data.message);
                    break;
            }
        },
        error: function () {
            showAlert('error', 'This resource is not available.');
        },
        complete: function () {
            setFormLoading($form, false);
            setButtonLoading($submitBtn, false);
        }
    });
});

function getUrlDispatch() {
    return $('#admin_label_id').val() === "" ? '/admins/save/' : '/admins/edit/' + $('#admin_label_id').val();
}

function showModal() {
    // Button text and css
    $('#admin_button_form').html('<i class="fas fa-user-plus mr-1"></i> Create Admin');
    $('#admin_button_form').removeClass();
    $('#admin_button_form').addClass('btn btn-primary');
    // Values of form
    $('#admin_label_id').val('');
    $('#admin_label_username').val('');
    $('#admin_label_email').val('');
    setPasswordFieldsRequired(true);
    //Validation of form
    $('#form_admin').removeClass();
    $('#form_admin').addClass('needs-validation');

    $('#admin_modal').modal('show');
}

$('#admin_table tbody').on('click', '#edit_admin_btn', function () {
    let data = lbrRowData(adminTable, this);
    $('#admin_button_form').html('<i class="far fa-edit mr-1"></i> Edit Admin');
    $('#admin_button_form').removeClass();
    $('#admin_button_form').addClass('btn btn-warning');
    $('#admin_label_id').val(data.id);
    $('#admin_label_username').val(data.username);
    $('#admin_label_email').val(data.email);
    setPasswordFieldsRequired(false);
    $('#form_admin').removeClass();
    $('#form_admin').addClass('needs-validation');
    $('#admin_modal').modal('show');
});

// On create the password is mandatory; on edit it is optional and
// blank fields keep the current password.
function setPasswordFieldsRequired(required) {
    $('#admin_label_password1, #admin_label_password2')
        .val('')
        .prop('required', required);
    if (required) {
        $('#admin_label_password1').attr('placeholder', 'At least 8 characters');
        $('#admin_label_password2').attr('placeholder', 'Repeat the password');
        $('#admin_password_hint').text('Minimum 8 characters, not entirely numeric and not too common.');
    } else {
        $('#admin_label_password1').attr('placeholder', 'Leave blank to keep current password');
        $('#admin_label_password2').attr('placeholder', 'Leave blank to keep current password');
        $('#admin_password_hint').text('Only fill this in to set a new password.');
    }
}

$('#admin_table tbody').on('click', '#remove_admin_btn', function () {
    let data = lbrRowData(adminTable, this);
    $('#admin_delete_value').val(data.id);
    $('#admin_to_delete').html(data.username);
    $('#admin_modal_delete').modal('show');
});

function deleteAdmin(btn) {
    var $form = $("#form_delete_admin");
    var formData = $form.serialize(); // before locking: disabled fields don't serialize
    setButtonLoading(btn, true);
    setFormLoading($form, true);
    $.ajax({
        url: '/admins/delete/',
        data: formData,
        type: "POST",
        success: function (data) {
            switch (parseInt(data.status)) {
                case 1:
                    adminTable.ajax.reload(null, false);
                    $('#admin_modal_delete').modal('hide');
                    showAlert(data.type, data.message);
                    break;
                case -1:
                    showAlert(data.type, data.message);
                    break;
                default:
                    showAlert('error', 'Action not complete.');
                    break;
            }
        },
        error: function () {
            showAlert('error', 'This resource is not available.');
        },
        complete: function () {
            setFormLoading($form, false);
            setButtonLoading(btn, false);
        }
    });
}

// Clear the form whenever the modal closes
$('#admin_modal').on('hidden.bs.modal', function () {
    var form = $('#form_admin')[0];
    if (form) {
        form.reset();
        $('#form_admin').removeClass('was-validated');
    }
});
