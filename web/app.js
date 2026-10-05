/* 第一次的人生 · 交互（原生 JS，约 3KB） */
(function(){
  'use strict';

  /* ---------- 导航：向下滑收起、向上滑露出 ---------- */
  var nav = document.querySelector('.nav');
  if (nav) {
    var lastY = window.scrollY, ticking = false;
    window.addEventListener('scroll', function(){
      if (ticking) return; ticking = true;
      requestAnimationFrame(function(){
        var y = window.scrollY, dy = y - lastY;
        if (dy > 6 && y > 140) nav.classList.add('hide');
        else if (dy < -6 || y < 60) nav.classList.remove('hide');
        lastY = y; ticking = false;
      });
    }, {passive:true});
  }

  /* ---------- 滚动进场：淡入 + 上移 20px ---------- */
  var reveals = document.querySelectorAll('.reveal');
  if (reveals.length && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(function(entries){
      entries.forEach(function(en){
        if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
      });
    }, {rootMargin:'0px 0px -8% 0px', threshold:0.05});
    reveals.forEach(function(el){ io.observe(el); });
  } else {
    reveals.forEach(function(el){ el.classList.add('in'); });
  }

  /* ---------- 首页：搜索 + 分段筛选 + 关键词 ---------- */
  var input = document.getElementById('q');
  if (!input) return;

  var state = { q:'', ev:'', eff:'', free:false };
  var rows = Array.prototype.slice.call(document.querySelectorAll('[data-row]'));
  var meta = document.getElementById('searchmeta');
  var empty = document.getElementById('empty');
  var groups = Array.prototype.slice.call(document.querySelectorAll('[data-group]'));
  var blocks = Array.prototype.slice.call(document.querySelectorAll('[data-block]'));
  var cards = Array.prototype.slice.call(document.querySelectorAll('.bento .card'));
  var total = rows.length;

  function match(el){
    if (state.ev && el.dataset.ev !== state.ev) return false;
    if (state.eff && el.dataset.eff !== state.eff) return false;
    if (state.free && el.dataset.free !== '1') return false;
    if (state.q && el.dataset.text.indexOf(state.q) < 0) return false;
    return true;
  }

  function render(){
    var shown = 0, cache = {};
    rows.forEach(function(el){
      var ok = match(el);
      el.hidden = !ok;
      if (ok) { shown++; cache[el.dataset.group] = (cache[el.dataset.group]||0) + 1; }
    });
    groups.forEach(function(g){ g.hidden = !cache[g.dataset.group]; });
    blocks.forEach(function(b){
      var any = b.querySelector('[data-group]:not([hidden])');
      b.hidden = !any;
    });
    if (cards.length){
      cards.forEach(function(c){
        var n = c.dataset.cat;
        var visible = b_has(cat_rows(n));
        c.hidden = !visible;
      });
    }
    function cat_rows(cat){ return rows.filter(function(r){ return r.dataset.cat === cat; }); }
    function b_has(list){ return list.some(function(r){ return !r.hidden; }); }

    if (meta){
      meta.textContent = (state.q || state.ev || state.eff || state.free)
        ? '找到 ' + shown + ' 条' + (state.q ? '（关键词：' + state.q + '）' : '')
        : '共 ' + total + ' 条 · 支持搜「退票」「工伤」「AED」这类具体的事';
    }
    if (empty) empty.hidden = shown !== 0;
  }

  input.addEventListener('input', function(){ state.q = input.value.trim().toLowerCase(); render(); });

  document.querySelectorAll('[data-filter="ev"]').forEach(function(btn){
    btn.addEventListener('click', function(){
      var v = btn.dataset.value;
      state.ev = (state.ev === v) ? '' : v;
      document.querySelectorAll('[data-filter="ev"]').forEach(function(b){ b.setAttribute('aria-pressed', String(b.dataset.value === state.ev)); });
      render();
    });
  });
  document.querySelectorAll('[data-filter="eff"]').forEach(function(btn){
    btn.addEventListener('click', function(){
      var v = btn.dataset.value;
      state.eff = (state.eff === v) ? '' : v;
      document.querySelectorAll('[data-filter="eff"]').forEach(function(b){ b.setAttribute('aria-pressed', String(b.dataset.value === state.eff)); });
      render();
    });
  });
  var freeBtn = document.querySelector('[data-filter="free"]');
  if (freeBtn) freeBtn.addEventListener('click', function(){
    state.free = !state.free;
    freeBtn.setAttribute('aria-pressed', String(state.free));
    render();
  });
  document.querySelectorAll('[data-kw]').forEach(function(btn){
    btn.addEventListener('click', function(){
      state.q = btn.dataset.kw.toLowerCase();
      input.value = btn.dataset.kw;
      render();
      var top = document.querySelector('.js-list-start');
      if (top) top.scrollIntoView({behavior:'smooth', block:'start'});
    });
  });
  var reset = document.getElementById('resetall');
  if (reset) reset.addEventListener('click', function(){
    state = { q:'', ev:'', eff:'', free:false };
    input.value = '';
    document.querySelectorAll('[aria-pressed]').forEach(function(b){ b.setAttribute('aria-pressed','false'); });
    render();
    input.focus();
  });

  render();
})();
