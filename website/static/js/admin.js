document.addEventListener('DOMContentLoaded', function () {
    // Modal de asignar técnico
    const asignarTecnicoModal = document.getElementById('asignarTecnicoModal');
    if (asignarTecnicoModal) {
        handleAssignTechnicianModal(asignarTecnicoModal);
    }

   
});

function handleAssignTechnicianModal(modal) {
    modal.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        const ticketId = button.getAttribute('data-ticket-id');
        const ticketTitle = button.getAttribute('data-ticket-title');

        const ticketDisplay = modal.querySelector('#ticket_display');
        const ticketIdInput = modal.querySelector('#ticket_id');

        if (ticketDisplay && ticketIdInput) {
            ticketDisplay.value = `#${ticketId} - ${ticketTitle}`;
            ticketIdInput.value = ticketId;
        }
    });

    const form = document.getElementById('assignTechnicianForm');
    if (form) {
        form.addEventListener('submit', function (event) {
            const tecnicoSelect = form.querySelector('select[name="tecnico_id"]');
            if (tecnicoSelect && tecnicoSelect.value === "") {
                event.preventDefault();
                alert('Por favor selecciona un técnico');
                return false;
            }
        });
    }
}

