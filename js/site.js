// ABR Pro Towing — mobile menu + form submit state
(function () {
  var btn = document.querySelector('.nav-toggle');
  var nav = document.getElementById('nav');
  if (btn && nav) {
    btn.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      btn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    });
  }
  document.querySelectorAll('.tow-form').forEach(function (f) {
    f.addEventListener('submit', function () {
      var b = f.querySelector('button[type="submit"]');
      if (b) { b.disabled = true; b.textContent = 'Sending…'; }
    });
  });
})();
