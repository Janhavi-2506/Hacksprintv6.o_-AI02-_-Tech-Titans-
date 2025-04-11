// Resume Screening Assistant - Custom JavaScript

// Document Ready Function
document.addEventListener('DOMContentLoaded', function() {
    // Fix for blank page issue in Replit
    document.body.style.display = 'block';
    document.body.style.visibility = 'visible';
    document.body.style.opacity = '1';
    document.body.style.backgroundColor = '#212529';
    document.body.style.color = '#f8f9fa';
    
    // Force display after a short delay
    setTimeout(function() {
        document.body.style.display = 'block';
        document.body.style.visibility = 'visible';
        document.body.style.opacity = '1';
        console.log('Forcing display of body content');
    }, 500);
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // File input enhancement
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            const fileName = e.target.files[0]?.name;
            const fileLabel = e.target.nextElementSibling;
            if (fileLabel && fileLabel.classList.contains('form-text')) {
                if (fileName) {
                    fileLabel.textContent = 'Selected file: ' + fileName;
                } else {
                    fileLabel.textContent = 'Accepted formats: PDF, DOCX (Max 16MB)';
                }
            }
        });
    });

    // Candidate status change highlight
    const statusSelect = document.getElementById('status');
    if (statusSelect) {
        const originalValue = statusSelect.value;
        statusSelect.addEventListener('change', function() {
            if (this.value !== originalValue) {
                this.classList.add('border-primary');
            } else {
                this.classList.remove('border-primary');
            }
        });
    }

    // Form validation enhancement
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Find the first invalid field and focus it
                const invalidFields = form.querySelectorAll(':invalid');
                if (invalidFields.length > 0) {
                    invalidFields[0].focus();
                }
            }
            
            form.classList.add('was-validated');
        }, false);
    });
});
