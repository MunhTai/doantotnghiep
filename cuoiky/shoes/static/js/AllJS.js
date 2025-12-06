// banner
document.addEventListener('DOMContentLoaded', function () {
  const banners = document.querySelector('.banners');
  const bannerImages = document.querySelectorAll('.banners img');
  const btnLeft = document.querySelector('.banner-btn-left');
  const btnRight = document.querySelector('.banner-btn-right');

  let currentIndex = 0;
  const totalBanners = bannerImages.length;
  const bannerWidth = 1024; // phải khớp CSS width

  function showBanner(index) {
    if (index < 0) {
      currentIndex = totalBanners - 1;
    } else if (index >= totalBanners) {
      currentIndex = 0;
    } else {
      currentIndex = index;
    }

    const offset = -currentIndex * bannerWidth;
    banners.style.transform = `translateX(${offset}px)`;
  }

  // Nút trái
  btnLeft.addEventListener('click', function () {
    showBanner(currentIndex - 1);
  });

  // Nút phải
  btnRight.addEventListener('click', function () {
    showBanner(currentIndex + 1);
  });

  // Tự động chuyển banner mỗi 5 giây
  setInterval(function () {
    showBanner(currentIndex + 1);
  }, 5000);
});

// sidebar
function toggleSidebar() {
  const sidebar = document.getElementById("sidebar");
  sidebar.classList.toggle("collapsed");
}

    document.querySelectorAll('.cart-items').forEach(item => {
    const decreaseBtn = item.querySelector('.decrease');
    const increaseBtn = item.querySelector('.increase');
    const quantitySpan = item.querySelector('.qty');

    let quantity = parseInt(quantitySpan.textContent);

    decreaseBtn.addEventListener('click', () => {
        if (quantity > 1) {
            quantity--;
            quantitySpan.textContent = quantity;
        }
    });

    increaseBtn.addEventListener('click', () => {
        quantity++;
        quantitySpan.textContent = quantity;
    });
});
