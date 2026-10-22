/* ==========================================================================
   JAIPUR LIVING - CLIENT INTERACTION ENGINE
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  // 1. CSRF Helper for Django AJAX
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  const csrftoken = getCookie('csrftoken');

  // 2. Search Dropdown Toggle
  const searchBtn = document.getElementById('searchToggleBtn');
  const searchDropdown = document.getElementById('searchDropdown');
  const searchInput = document.getElementById('mainSearchInput');

  if (searchBtn && searchDropdown) {
    searchBtn.addEventListener('click', (e) => {
      e.preventDefault();
      searchDropdown.classList.toggle('active');
      if (searchDropdown.classList.contains('active')) {
        setTimeout(() => searchInput && searchInput.focus(), 100);
      }
    });

    document.addEventListener('click', (e) => {
      if (!searchDropdown.contains(e.target) && !searchBtn.contains(e.target)) {
        searchDropdown.classList.remove('active');
      }
    });
  }

  // 3. Carousel Navigation
  document.querySelectorAll('.carousel-container').forEach(carousel => {
    const track = carousel.querySelector('.product-carousel-track');
    const prevBtn = carousel.querySelector('.carousel-btn.prev');
    const nextBtn = carousel.querySelector('.carousel-btn.next');

    if (track && prevBtn && nextBtn) {
      prevBtn.addEventListener('click', () => {
        track.scrollBy({ left: -340, behavior: 'smooth' });
      });
      nextBtn.addEventListener('click', () => {
        track.scrollBy({ left: 340, behavior: 'smooth' });
      });
    }
  });

  // 4. Shoppable Lifestyle Hotspot Drawer Toggle
  const hotspotBtn = document.getElementById('shoppableHotspotBtn');
  const shoppableDrawer = document.getElementById('shoppableDrawer');
  const shoppableClose = document.getElementById('shoppableDrawerClose');

  if (hotspotBtn && shoppableDrawer) {
    hotspotBtn.addEventListener('click', () => {
      shoppableDrawer.classList.toggle('active');
    });
  }
  if (shoppableClose && shoppableDrawer) {
    shoppableClose.addEventListener('click', () => {
      shoppableDrawer.classList.remove('active');
    });
  }

  // 5. Trending Tabs Filtering
  const tabBtns = document.querySelectorAll('.trending-tabs .tab-btn');
  const productCards = document.querySelectorAll('.trending-grid-section .product-card');

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const filter = btn.dataset.filter;

      productCards.forEach(card => {
        if (filter === 'all' || card.dataset.category === filter || card.dataset.material === filter) {
          card.style.display = 'flex';
        } else {
          card.style.display = 'none';
        }
      });
    });
  });

  // 6. Cart Drawer Functionality
  const cartBtn = document.getElementById('cartDrawerOpenBtn');
  const cartOverlay = document.getElementById('cartDrawerOverlay');
  const cartDrawer = document.getElementById('cartDrawer');
  const cartCloseBtn = document.getElementById('cartDrawerCloseBtn');
  const cartBadge = document.getElementById('cartCountBadge');
  const cartItemsContainer = document.getElementById('cartItemsList');
  const cartSubtotalEl = document.getElementById('cartSubtotalAmount');
  const freeShippingBar = document.getElementById('freeShippingProgressBar');
  const freeShippingText = document.getElementById('freeShippingBarText');

  function openCart() {
    if (cartOverlay && cartDrawer) {
      cartOverlay.classList.add('active');
      cartDrawer.classList.add('active');
      fetchCart();
    }
  }

  function closeCart() {
    if (cartOverlay && cartDrawer) {
      cartOverlay.classList.remove('active');
      cartDrawer.classList.remove('active');
    }
  }

  if (cartBtn) cartBtn.addEventListener('click', (e) => { e.preventDefault(); openCart(); });
  if (cartCloseBtn) cartCloseBtn.addEventListener('click', closeCart);
  if (cartOverlay) cartOverlay.addEventListener('click', closeCart);

  function updateCartUI(cartData) {
    if (cartBadge) cartBadge.textContent = cartData.total_qty;
    if (cartSubtotalEl) cartSubtotalEl.textContent = `$${cartData.total_price.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;

    // Free shipping bar ($500 threshold)
    if (freeShippingBar && freeShippingText) {
      const pct = Math.min(100, (cartData.total_price / 500) * 100);
      freeShippingBar.style.width = `${pct}%`;
      if (cartData.has_free_shipping) {
        freeShippingText.innerHTML = '🎉 You qualified for <strong>FREE Complimentary White-Glove Shipping!</strong>';
      } else {
        freeShippingText.innerHTML = `Add <strong>$${cartData.amount_needed_for_free_shipping.toFixed(2)}</strong> more to unlock Free White-Glove Shipping`;
      }
    }

    if (cartItemsContainer) {
      if (cartData.items.length === 0) {
        cartItemsContainer.innerHTML = '<div class="cart-empty-message"><p>Your bag is currently empty.</p><a href="/rugs/" class="btn-luxury-primary" style="margin-top:16px;">Explore Rugs</a></div>';
      } else {
        cartItemsContainer.innerHTML = cartData.items.map(item => `
          <div class="cart-item-row" data-key="${item.key}">
            <img src="${item.image}" alt="${item.name}">
            <div class="cart-item-info">
              <div class="cart-item-info-title">${item.name}</div>
              <div class="cart-item-info-meta">${item.size} • ${item.color}</div>
              <div class="cart-item-info-price">$${item.subtotal.toLocaleString('en-US', { minimumFractionDigits: 2 })} (Qty: ${item.quantity})</div>
            </div>
            <button class="cart-item-remove-btn" onclick="removeCartItem('${item.key}')">Remove</button>
          </div>
        `).join('');
      }
    }
  }

  async function fetchCart() {
    try {
      const res = await fetch('/api/cart/');
      if (res.ok) {
        const data = await res.json();
        updateCartUI(data);
      }
    } catch (err) {
      console.error('Error fetching cart:', err);
    }
  }

  window.removeCartItem = async function(key) {
    try {
      const res = await fetch('/api/cart/', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ key: key }),
      });
      if (res.ok) {
        const data = await res.json();
        updateCartUI(data.cart);
      }
    } catch (err) {
      console.error('Error removing item:', err);
    }
  };

  window.addToCartDirect = async function(productId, size, color, qty = 1) {
    try {
      const res = await fetch('/api/cart/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
          product_id: productId,
          size: size,
          color: color,
          quantity: qty,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        updateCartUI(data.cart);
        openCart();
      }
    } catch (err) {
      console.error('Error adding to cart:', err);
    }
  };

  // 7. Wishlist / Project List Toggle
  const wishlistBadge = document.getElementById('wishlistCountBadge');
  window.toggleWishlist = async function(btn, productId) {
    try {
      const res = await fetch('/api/wishlist/toggle/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ product_id: productId }),
      });
      if (res.ok) {
        const data = await res.json();
        if (data.status === 'added') {
          btn.classList.add('active');
        } else {
          btn.classList.remove('active');
        }
        if (wishlistBadge) wishlistBadge.textContent = data.count;
      }
    } catch (err) {
      console.error('Error toggling wishlist:', err);
    }
  };

  // 8. Product Card Direct Navigation (Clicking any product opens Product Detail Page)
  document.addEventListener('click', (e) => {
    const card = e.target.closest('.product-card');
    if (card && !e.target.closest('.wishlist-btn') && !e.target.closest('.btn-quick-add')) {
      const link = card.querySelector('a.product-card-name') || card.querySelector('a');
      if (link && link.href) {
        window.location.href = link.href;
      }
    }
  });

  window.openQuickView = async function(productId) {
    try {
      const res = await fetch(`/api/products/${productId}/quick-view/`);
      if (res.ok) {
        const prod = await res.json();
        // Redirect directly to product detail page
        window.location.href = `/rugs/${prod.name.toLowerCase().replace(/[^a-z0-9]+/g, '-')}/`;
      }
    } catch (err) {
      console.error('Error redirecting to product:', err);
    }
  };

  // 9. Trade Application Modal
  const tradeModal = document.getElementById('tradeApplicationModal');
  const tradeModalClose = document.getElementById('tradeModalCloseBtn');
  const tradeForm = document.getElementById('tradeApplicationForm');
  const tradeTriggers = document.querySelectorAll('.trade-application-trigger');

  function openTradeModal() {
    if (tradeModal) tradeModal.classList.add('active');
  }
  function closeTradeModal() {
    if (tradeModal) tradeModal.classList.remove('active');
  }

  tradeTriggers.forEach(btn => btn.addEventListener('click', (e) => {
    e.preventDefault();
    openTradeModal();
  }));

  if (tradeModalClose) tradeModalClose.addEventListener('click', closeTradeModal);
  if (tradeModal) tradeModal.addEventListener('click', (e) => {
    if (e.target === tradeModal) closeTradeModal();
  });

  if (tradeForm) {
    tradeForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(tradeForm);
      const payload = Object.fromEntries(formData.entries());

      try {
        const res = await fetch('/api/trade/apply/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
          },
          body: JSON.stringify(payload),
        });
        const data = await res.json();
        if (res.ok) {
          alert(data.message);
          tradeForm.reset();
          closeTradeModal();
        } else {
          alert(data.message || 'Error submitting application.');
        }
      } catch (err) {
        console.error('Error submitting trade application:', err);
      }
    });
  }

  // 10. Newsletter Subscription
  const newsletterForm = document.getElementById('newsletterSubscribeForm');
  if (newsletterForm) {
    newsletterForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const emailInput = newsletterForm.querySelector('input[name="email"]');
      const feedbackEl = document.getElementById('newsletterFeedback');

      try {
        const res = await fetch('/api/newsletter/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
          },
          body: JSON.stringify({ email: emailInput.value }),
        });
        const data = await res.json();
        if (res.ok) {
          if (feedbackEl) {
            feedbackEl.className = 'newsletter-feedback success';
            feedbackEl.textContent = data.message;
          }
          newsletterForm.reset();
        } else {
          if (feedbackEl) {
            feedbackEl.className = 'newsletter-feedback error';
            feedbackEl.textContent = data.message;
          }
        }
      } catch (err) {
        console.error('Error subscribing to newsletter:', err);
      }
    });
  }

  // Mobile Menu Drawer
  const mobileMenuBtn = document.getElementById('mobileMenuToggleBtn');
  const mobileDrawer = document.getElementById('mobileNavDrawer');
  const mobileDrawerClose = document.getElementById('mobileDrawerCloseBtn');

  if (mobileMenuBtn && mobileDrawer) {
    mobileMenuBtn.addEventListener('click', () => {
      mobileDrawer.classList.toggle('active');
    });
  }
  if (mobileDrawerClose && mobileDrawer) {
    mobileDrawerClose.addEventListener('click', () => {
      mobileDrawer.classList.remove('active');
    });
  }
});
