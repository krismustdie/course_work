console.log("Script loaded");

function handleImageError(imgElement) {
  // Пытаемся заменить изображение на запасное
  imgElement.src =  imgElement.dataset.fallback+imgElement.alt;
  console.log(imgElement.dataset.fallback);
  // Если запасное тоже не загрузилось, можно добавить обработчик на этот случай
  imgElement.onerror = function() {
    console.error('Не удалось загрузить запасное изображение', imgElement);
    // Можно скрыть изображение или показать placeholder
  };
}

function handleBackdropError(backdropElement) {
  // Пытаемся заменить изображение на запасное
  backdropElement.src =  backdropElement.dataset.fallback;
  console.log(backdropElement.dataset.fallback);
  // Если запасное тоже не загрузилось, можно добавить обработчик на этот случай
  backdropElement.onerror = function() {
    console.error('Не удалось загрузить запасное изображение', backdropElement);
    // Можно скрыть изображение или показать placeholder
  };
}
