var reservationTable;

$(document).ready(function () {
    reservationTable = $('#reservation_table').DataTable({
        'ajax': '/reserve/get/',
        'processing': true,
        'language': { 'processing': LBR_DT_PROCESSING },
        'columns': [
            { 'data': 'name' },
            { 'data': 'dni' },
            { 'data': 'book' },
            { 'data': 'start_date' },
            { 'data': 'end_date' },
            {
                'data': 'status',
                'render': function (data) { return renderStatusBadge(data); }
            },
            {
                'data': null,
                'orderable': false,
                'width': '6%',
                'render': function (data, type, row) {
                    if (row.status === 'reserved') {
                        return '<button id="reservation_checkout_btn" class="btn btn-primary btn-sm lbr-action-btn" title="Mark as Checked Out"><i class="fas fa-hand-holding-open"></i></button>';
                    }
                    if (row.status === 'checked_out' || row.status === 'overdue') {
                        return '<button id="reservation_return_btn" class="btn btn-success btn-sm lbr-action-btn" title="Mark as Returned"><i class="fas fa-undo-alt"></i></button>';
                    }
                    return '';
                }
            },
            {
                'data': null,
                'orderable': false,
                'width': '5%',
                'defaultContent': '<button id="reservation_delete_btn" class="btn btn-danger btn-sm lbr-action-btn" title="Clear Reservation"><i class="fas fa-trash-alt"></i></button>'
            }
        ]
    });

    $('#reservation_table tbody').on('click', '#reservation_checkout_btn', function () {
        var row = reservationTable.row($(this).parents('tr')).data();
        updateReservationStatus(row.id, 'checked_out', this);
    });

    $('#reservation_table tbody').on('click', '#reservation_return_btn', function () {
        var row = reservationTable.row($(this).parents('tr')).data();
        updateReservationStatus(row.id, 'returned', this);
    });

    $('#reservation_table tbody').on('click', '#reservation_delete_btn', function () {
        var row = reservationTable.row($(this).parents('tr')).data();
        $('#delete_reservation_id').val(row.id);
        $('#reservation_name_to_delete').text(row.name + ' — ' + row.book);
        $('#deleteReservationModal').modal('show');
    });

    $('#form_delete_reservation').submit(function (event) {
        event.preventDefault();
        var $form = $(this);
        var formData = $form.serialize(); // before locking: disabled fields don't serialize
        var $submitBtn = $form.find('button[type="submit"]');
        setButtonLoading($submitBtn, true);
        setFormLoading($form, true);
        $.ajax({
            url: '/reserve/delete/',
            type: 'POST',
            data: formData,
            success: function (data) {
                switch (parseInt(data.status)) {
                    case 1:
                        $('#deleteReservationModal').modal('hide');
                        reservationTable.ajax.reload(null, false);
                        showAlert(data.type, data.message);
                        break;
                    case -1:
                        showAlert(data.type, data.message);
                        break;
                }
            },
            error: function () {
                showAlert('error', 'Could not clear reservation.');
            },
            complete: function () {
                setFormLoading($form, false);
                setButtonLoading($submitBtn, false);
            }
        });
    });
});

function renderStatusBadge(status) {
    var config = {
        'reserved':    { cls: 'lbr-status-reserved',    label: 'Reserved' },
        'checked_out': { cls: 'lbr-status-checked-out', label: 'Checked Out' },
        'returned':    { cls: 'lbr-status-returned',    label: 'Returned' },
        'overdue':     { cls: 'lbr-status-overdue',     label: 'Overdue' }
    };
    var c = config[status] || { cls: '', label: status };
    return '<span class="lbr-status-badge ' + c.cls + '">' + c.label + '</span>';
}

function setRowActionsLocked(locked) {
    // Lock every row action so a second update can't start mid-request;
    // the spinning button is skipped (setButtonLoading owns its state).
    $('#reservation_table .lbr-action-btn').each(function () {
        if (!$(this).data('lbrLoading')) {
            $(this).prop('disabled', locked);
        }
    });
}

function updateReservationStatus(reservationId, newStatus, btn) {
    setButtonLoading(btn, true);
    setRowActionsLocked(true);
    $.ajax({
        url: '/reserve/update/' + reservationId + '/',
        type: 'POST',
        data: {
            csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').first().val(),
            status: newStatus
        },
        success: function (data) {
            switch (parseInt(data.status)) {
                case 1:
                    // The reload redraws the rows, replacing all locked buttons
                    reservationTable.ajax.reload(null, false);
                    showAlert(data.type, data.message);
                    break;
                case -1:
                    setButtonLoading(btn, false);
                    setRowActionsLocked(false);
                    showAlert(data.type, data.message);
                    break;
            }
        },
        error: function () {
            setButtonLoading(btn, false);
            setRowActionsLocked(false);
            showAlert('error', 'Could not update reservation.');
        }
    });
}
