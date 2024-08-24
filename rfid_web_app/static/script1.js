document.addEventListener('DOMContentLoaded', () => {
    const addCode = document.querySelector('#code');
    const addItem = document.querySelector('#item');
    const additionResult = document.getElementById('to_be_added');

    const clearButton = document.getElementById('Clear_RFID');
    const eraseButton = document.getElementById('Clear_Name');
    const saveButton = document.getElementById('Submit_Save');
    
    function updateInfo() {
        const codeValue = addCode.value.trim();
        const itemValue = addItem.value.trim();
         
        if (!codeValue || !itemValue) {
            additionResult.innerHTML.append("Please fill in both fields.");
            return;  // Stop execution if any field is empty
        }
        const formData = new FormData();
        formData.append('code', codeValue);
        formData.append('item', itemValue);
        fetch('/add_code_name', { 
            method: 'POST', body: formData
        })
        .then(response => response.text())
        .then(data => { additionResult.innerHTML = data.replace(/\n/g, '<br>'); })
        .catch(error => console.error('Error:', error));
    } 
    addCode.addEventListener('input', updateInfo);
    addItem.addEventListener('input', updateInfo);
    
    clearButton.addEventListener('click', function() {
        addCode.value = ''; 
    });

    eraseButton.addEventListener('click', function() {
        addItem.value = ''; 
    });

    saveButton.addEventListener('click', function() {
        fetch('/save_to_file', {
            method: 'POST',
        })
        .then(response => response.text())
        .then(data => {
            document.querySelector('#to_be_added').innerHTML = data.replace(/\n/g, '<br>');
            addCode.value = '';
        })
        .catch(error => console.error('Error:', error));
    }); 
    
});