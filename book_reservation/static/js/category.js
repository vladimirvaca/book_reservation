
var categoryTable = $('#category_table').DataTable({
    'ajax': './get',
    'columns': [{
            'data': 'category'
        },
        {
            'data': 'description'
        },
        {},
        {}
    ],
    "columnDefs": [{
            'targets': -2,
            'data': '',
            'width': '5%',
            'defaultContent': '<button id="edit_category_btn" class="btn btn-secondary btn-sm"><span class="far fa-edit fa-xs"></button>'
        },
        {
            'targets': -1,
            'data': '',
            'width': '5%',
            'defaultContent': '<button id="remove_category_btn" class="btn btn-danger btn-sm"><span class="fas fa-trash-alt fa-xs"></button>'
        }
    ]
});


$('#form_category').submit(function (event) {
    event.preventDefault();
    $.ajax({
        url: getUrlDispatch(),
        type: "POST",
        data: $("#form_category").serialize(),
        success: function (data) {
            switch (parseInt(data.status)) {
                case -1:
                    showAlert(data.type, data.message);
                    break;
                case 1:
                    $('#category_modal').modal('hide')
                    categoryTable.ajax.reload(null, false);
                    showAlert(data.type, data.message);
                    break;
            }
        },
        error: function () {
            $.notify('This resource is not avalaible', 'error');
        }
    });
});

function getUrlDispatch() {
    return $('#category_label_id').val() === "" ? '/category/save/' : '/category/edit/' + $('#category_label_id').val();
}

$('#category_table tbody').on('click', '#edit_category_btn', function () {
    let data = categoryTable.row($(this).parents('tr')).data();
    $('#category_button_form').html('Edit');
    $('#category_button_form').removeClass();
    $('#category_button_form').addClass('btn btn-warning');
    $('#category_label_id').val(data.id);
    $('#category_label_category').val(data.category);
    $('#category_label_description').val(data.description);
    $('#category_modal').modal('show');
});

$('#category_table tbody').on('click', '#remove_category_btn', function () {
    let data = categoryTable.row($(this).parents('tr')).data();
    $('#category_delete_value').val(data.id);
    $('#category_to_delete').html(data.category);
    $('#category_modal_delete').modal('show');
});

function deleteCategory() {
    $.ajax({
        url: '/category/delete/',
        data: $("#form_delete_category").serialize(),
        type: "POST",
        success: function (data) {
            switch (parseInt(data.status)) {
                case 1:
                    categoryTable.ajax.reload(null, false);
                    $('#category_modal_delete').modal('hide');
                    showAlert(data.type, data.message);
                    break;
                default:
                    showAlert('error', 'Action not complete.');
                    break;

            }
        },
        error: function () {
            $.notify('This resource is not avalaible', 'error');
        }
    });
}

function showModal() {
    // Button text and css
    $('#category_button_form').html('Save');
    $('#category_button_form').removeClass();
    $('#category_button_form').addClass('btn btn-primary');
    // Values of form
    $('#category_label_id').val('');
    $('#category_label_category').val('');
    $('#category_label_description').val('');
    $('#category_label_description').val('');
    //search_label_category
    $('#category_modal').modal('show');
    //Validation of form
    $('#form_category').removeClass();
    $('#form_category').addClass('needs-validation');
}