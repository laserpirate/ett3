(function(){var c=[].slice.call(document.querySelectorAll('.card button')),lb=document.getElementById('lb'),im=lb.querySelector('img'),
nm=lb.querySelector('.bar span'),fu=lb.querySelector('.full'),i=0;
function show(k){i=(k+c.length)%c.length;var b=c[i];im.src=b.dataset.full;im.alt=b.dataset.name;nm.textContent=b.dataset.name+'  ('+(i+1)+' of '+c.length+')';fu.href=b.dataset.full;lb.classList.add('on');}
function hide(){lb.classList.remove('on');im.removeAttribute('src');c[i].focus();}
c.forEach(function(b,k){b.addEventListener('click',function(){show(k);});});
lb.querySelector('.x').addEventListener('click',hide);lb.querySelector('.pv').addEventListener('click',function(){show(i-1);});
lb.querySelector('.nx').addEventListener('click',function(){show(i+1);});
lb.addEventListener('click',function(e){if(e.target===lb||e.target.classList.contains('fig'))hide();});
document.addEventListener('keydown',function(e){if(!lb.classList.contains('on'))return;if(e.key==='Escape')hide();
else if(e.key==='ArrowRight')show(i+1);else if(e.key==='ArrowLeft')show(i-1);});})();
