var bookTable = $('#book_table').DataTable({
    'ajax': './get',
    'responsive': true,
    'processing': true,
    'language': { 'processing': LBR_DT_PROCESSING },
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
        'defaultContent': '<button id="edit_book_btn" class="btn btn-secondary btn-sm"><i class="far fa-edit"></i></button>'
    },
    {
        'targets': -1,
        'data': '',
        'width': '5%',
        'defaultContent': '<button id="remove_book_btn" class="btn btn-danger btn-sm"><i class="fas fa-trash-alt"></i></button>'
    }]
});

$("#search_label_category").keyup(function () {
    loadSearchCategories();
});

function loadSearchCategories() {
    var $select = $("#select_category");
    $select.empty().append(new Option('Searching categories…', ''));
    $.ajax({
        url: "../category/search",
        type: "GET",
        data: { criteria: $("#search_label_category").val() },
        success: function (data) {
            $select.empty();
            if (data.length > 0) {
                for (var i = 0; i < data.length; i++) {
                    $select.append(new Option(data[i].category, data[i].id))
                }
            } else {
                $select.append(new Option('No results ..', ''))
            }
        },
        error: function () {
            $select.empty().append(new Option('Could not load categories', ''));
            showAlert('error', 'This resource is not available.');
        }
    });
}

$('#form_book').submit(function (event) {
    event.preventDefault();
    var $form = $(this);
    var formData = $form.serialize(); // before locking: disabled fields don't serialize
    var $submitBtn = $('#book_button_form');
    setButtonLoading($submitBtn, true);
    setFormLoading($form, true);
    $.ajax({
        url: getUrlDispatch(),
        type: "POST",
        data: formData,
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
            showAlert('error', 'This resource is not available.');
        },
        complete: function () {
            setFormLoading($form, false);
            setButtonLoading($submitBtn, false);
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
    let data = lbrRowData(bookTable, this);
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
    let data = lbrRowData(bookTable, this);
    $('#book_delete_value').val(data.id);
    $('#book_to_delete').html(data.category);
    $('#book_modal_delete').modal('show');
});


function deleteBook(btn) {
    var $form = $("#form_delete_book");
    var formData = $form.serialize(); // before locking: disabled fields don't serialize
    setButtonLoading(btn, true);
    setFormLoading($form, true);
    $.ajax({
        url: '/book/delete/',
        data: formData,
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
            showAlert('error', 'This resource is not available.');
        },
        complete: function () {
            setFormLoading($form, false);
            setButtonLoading(btn, false);
        }
    });
}
