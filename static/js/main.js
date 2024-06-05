
var imgs = document.querySelectorAll('.card-img');
for (let i = 0; i < imgs.length; i++) {
  imgs[i].addEventListener('error', function handleError() {
    let name = imgs[i].getAttribute('alt')
    imgs[i].src="https://placehold.co/300x450?text="+name
    console.log(imgs[i].src);
  })
}

