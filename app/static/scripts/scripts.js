document.addEventListener('DOMContentLoaded', function () {
    const recipeTitles = document.querySelectorAll('.recipe-title');
    recipeTitles.forEach((title, index) => {
        title.addEventListener('click', function () {
            const detailsId = `recipe-details-${index}`;
            const details = document.getElementById(detailsId);
            if (details) {
                details.style.display = details.style.display === 'none' ? 'block' : 'none';
            }
        });
    });


    const modal = document.getElementById('myModal');
    const closeModalButton = document.querySelector('.close');

    if (modal && closeModalButton) {

        closeModalButton.addEventListener('click', function () {
            modal.style.display = 'none';
        });


        window.addEventListener('click', function (event) {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });
    }


    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape' && modal && modal.style.display === 'block') {
            modal.style.display = 'none';
        }
    });
});
