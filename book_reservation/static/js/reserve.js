
// Load books and set date defaults when the modal opens
$('#reserve_modal').on('show.bs.modal', function () {
    var today = new Date().toISOString().split('T')[0];
    var tomorrow = new Date(Date.now() + 86400000).toISOString().split('T')[0];

    $('#reserve_start_date').attr('min', today).val(today);
    $('#reserve_end_date').attr('min', tomorrow).val('');

    var $select = $('#reserve_book');
    $select.empty().append(new Option('Loading books…', ''));

    $.ajax({
        url: '/reserve/books/',
        type: 'GET',
        success: function (data) {
            $select.empty();
            if (data.length > 0) {
                $select.append(new Option('Select a book…', ''));
                for (var i = 0; i < data.length; i++) {
                    $select.append(
                        new Option(data[i].name + '  ·  ' + data[i].number_serie, data[i].id)
                    );
                }
            } else {
                $select.append(new Option('No books available at the moment', ''));
            }
        },
        error: function () {
            $select.empty().append(new Option('Could not load books', ''));
            $.notify('Could not load the book list.', 'error');
        }
    });
});

// Keep end_date min in sync with start_date selection
$('#reserve_start_date').on('change', function () {
    var start = $(this).val();
    if (start) {
        var next = new Date(start + 'T00:00:00');
        next.setDate(next.getDate() + 1);
        var minEnd = next.toISOString().split('T')[0];
        var $end = $('#reserve_end_date');
        $end.attr('min', minEnd);
        if ($end.val() && $end.val() <= start) {
            $end.val('');
        }
    }
});

// Reset form when modal closes
$('#reserve_modal').on('hidden.bs.modal', function () {
    $('#form_reserve')[0].reset();
    $('#reserve_book').empty().append(new Option('Loading books…', ''));
    $('#form_reserve').removeClass('was-validated');
});

// Submit reservation
$('#form_reserve').submit(function (event) {
    event.preventDefault();

    $.ajax({
        url: '/reserve/save/',
        type: 'POST',
        data: $('#form_reserve').serialize(),
        success: function (data) {
            switch (parseInt(data.status)) {
                case 1:
                    $('#reserve_modal').modal('hide');
                    showAlert(data.type, data.message);
                    break;
                case -1:
                    showAlert(data.type, data.message);
                    break;
            }
        },
        error: function () {
            $.notify('This resource is not available.', 'error');
        }
    });
});
