//date picker animations

const dateEl = document.getElementById('id_date');

M.Datepicker.init(dateEl, {
    format: 'yyyy-mm-dd',
    defaultDate: new Date(),
    setDefaultDate: true,
    autoClose: true
});

// select widget animations

const selectEl = document.getElementById('id_meal');

M.FormSelect.init(selectEl);