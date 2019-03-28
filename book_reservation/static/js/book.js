var bookTable = $('#book_table').DataTable({
    'ajax': './get',
    'columns': [{
        'data': 'number_serie',
    },
    {
        'data': 'name'
    },
    {
        'data': 'category'
    },
    {
        'data': 'resume'
    },
    {},
    {}
    ],
    "columnDefs": [{
        'targets': -2,
        'data': '',
        'width': '5%',
        'defaultContent': '<button id="edit_book_btn" class="btn btn-secondary btn-sm"><span class="far fa-edit fa-xs"></button>'
    },
    {
        'targets': -1,
        'data': '',
        'width': '5%',
        'defaultContent': '<button id="remove_book_btn" class="btn btn-danger btn-sm"><span class="fas fa-trash-alt fa-xs"></button>'
    }]
});

$("#search_label_category").keyup(function () {
    $("#select_category").empty();
    loadSearchCategories();
});

function loadSearchCategories() {
    $.ajax({
        url: "../category/search",
        type: "GET",
        data: { criteria: $("#search_label_category").val() },
        success: function (data) {
            if (data.length > 0) {
                for (var i = 0; i < data.length; i++) {
                    $("#select_category").append(new Option(data[i].category, data[i].id))
                }
            } else {
                $("#select_category").append(new Option('No results ..', ''))
            }
        },
        error: function () {
            $.notify('This resource is not avalaible', 'error');
        }
    });
}

$('#form_book').submit(function (event) {
    event.preventDefault();
    $.ajax({
        url: getUrlDispatch(),
        type: "POST",
        data: $("#form_book").serialize(),
        success: function (data) {
            switch (parseInt(data.status)) {
                case -1:
                    showAlert(data.type, data.message);
                    break;
                case 1:
                    $('#book_modal').modal('hide')
                    bookTable.ajax.reload(null, false);
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
    return $('#book_label_id').val() === "" ? './save/' : './edit/' + $('#book_label_id').val();
}

function showModal() {
    // Button text and css
    $('#book_button_form').html('Save');
    $('#book_button_form').removeClass();
    $('#book_button_form').addClass('btn btn-primary');
    // Values of form
    $('#book_label_id').val('');
    loadSearchCategories();
    $('#book_label_name').val('');
    $('#category_label_serial_number').val('');
    $('#search_label_category').val('');
    $('#book_label_resume').val('');
    //Validation of form
    $('#form_book').removeClass();
    $('#form_book').addClass('needs-validation');

    $('#book_modal').modal('show');
}

$('#book_table tbody').on('click', '#edit_book_btn', function () {
    let data = bookTable.row($(this).parents('tr')).data();
    $('#book_button_form').html('Edit');
    $('#book_button_form').removeClass();
    $('#book_button_form').addClass('btn btn-warning');
    $('#book_label_id').val(data.id);
    $('#category_label_serial_number').val(data.number_serie);
    $('#select_category').val(data.category);
    $('#book_label_name').val(data.category);
    $('#book_label_resume').val(data.resume);
    $('#book_modal').modal('show');
});

$('#book_table tbody').on('click', '#remove_book_btn', function () {
    let data = bookTable.row($(this).parents('tr')).data();
    $('#book_delete_value').val(data.id);
    $('#book_to_delete').html(data.category);
    $('#book_modal_delete').modal('show');
});


function deleteBook() {
    $.ajax({
        url: '/book/delete/',
        data: $("#form_delete_book").serialize(),
        type: "POST",
        success: function (data) {
            switch (parseInt(data.status)) {
                case 1:
                    bookTable.ajax.reload(null, false);
                    $('#book_modal_delete').modal('hide');
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
