// Wait for the DOM to be loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Countdown timer for each capsule that hasn't been opened yet
    const countdownElements = document.querySelectorAll('.countdown-timer');
    if (countdownElements.length > 0) {
        countdownElements.forEach(element => {
            const openDate = new Date(element.getAttribute('data-open-date'));
            
            // Update the countdown every second
            const countdownInterval = setInterval(function() {
                const now = new Date().getTime();
                const distance = openDate - now;
                
                // If the date has passed, stop the countdown
                if (distance < 0) {
                    clearInterval(countdownInterval);
                    element.innerHTML = 'Ready to open!';
                    return;
                }
                
                // Calculate time remaining
                const days = Math.floor(distance / (1000 * 60 * 60 * 24));
                const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                const seconds = Math.floor((distance % (1000 * 60)) / 1000);
                
                // Display the countdown
                element.innerHTML = `${days}d ${hours}h ${minutes}m ${seconds}s`;
            }, 1000);
        });
    }
    
    // Form validation for capsule creation
    const capsuleForm = document.querySelector('#capsule-form');
    if (capsuleForm) {
        capsuleForm.addEventListener('submit', function(event) {
            const openDateInput = document.querySelector('#id_open_date');
            if (openDateInput) {
                const openDate = new Date(openDateInput.value);
                const now = new Date();
                
                if (openDate <= now) {
                    event.preventDefault();
                    const errorElement = document.createElement('div');
                    errorElement.classList.add('alert', 'alert-danger');
                    errorElement.textContent = 'The open date must be in the future.';
                    openDateInput.parentNode.insertBefore(errorElement, openDateInput);
                }
            }
        });
    }
    
    // Preview uploaded images
    const imageInput = document.querySelector('#id_image');
    const imagePreview = document.querySelector('#image-preview');
    
    if (imageInput && imagePreview) {
        imageInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    imagePreview.innerHTML = `<img src="${e.target.result}" class="img-fluid rounded">`;
                    imagePreview.classList.remove('d-none');
                }
                
                reader.readAsDataURL(this.files[0]);
            }
        });
    }
});
