function declineWord(num, word) {
  const lastDigit = num % 10;
  const isException = (num % 100 >= 11 && num % 100 <= 14);
  if (lastDigit === 1 && !isException) return word;
  if (lastDigit >= 2 && lastDigit <= 4 && !isException) return word + 'а';
  return word + 'ов';
}

async function loadStatsData(timespan) {
  try {
    const response = await fetch(link+timespan, {
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'include'
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Ошибка при загрузке данных:', error);
    return null;
  }
}

function displayStats(data) {
  if (!data) return;
  
  // количество часов
  const totalHours_number = document.getElementById('totalHours_number');
  const totalHours_title = document.getElementById('totalHours_title');
  totalHours_number.innerText = Math.floor(data.watchtime / 60);
  totalHours_title.innerText = declineWord(totalHours_number.innerText, "час");

  // количество фильмов
  const totalMovies_number = document.getElementById('totalMovies_number');
  const totalMovies_title = document.getElementById('totalMovies_title');
  totalMovies_number.innerText = data.movies_count;
  totalMovies_title.innerText = declineWord(totalMovies_number.innerText, "фильм");

  // количество сериалов
  const totalSeries_number = document.getElementById('totalSeries_number');
  const totalSeries_title = document.getElementById('totalSeries_title');
  totalSeries_number.innerText = data.series_count;
  totalSeries_title.innerText = declineWord(totalSeries_number.innerText, "сериал");

  // количество жанров
  const totalGenres_number = document.getElementById('totalGenres_number');
  const totalGenres_title = document.getElementById('totalGenres_title');
  totalGenres_number.innerText = (new Set(data.genre_counts.split(','))).size - 1;
  totalGenres_title.innerText = declineWord(totalGenres_number.innerText, "жанр");
}

async function initStats() {
  const defaultTimespan = 'month'; // Значение по умолчанию
  
  const initialData = await loadStatsData(defaultTimespan);
  displayStats(initialData);
  
  const dropdownItems = document.querySelectorAll('.dropdown-item');
  const statsLink = document.getElementById('stats-link');
  const statsButton = document.getElementById('stats-selector');
  
  dropdownItems.forEach((item) => {
    item.addEventListener('click', async function(e) {
      e.preventDefault();
      const timespan = this.getAttribute('data-timespan');
      const text = this.textContent;
      
      statsLink.href =stats_link+timespan;
      statsButton.textContent = text;
      
      const newData = await loadStatsData(timespan);
      displayStats(newData);
    });
  });
}

document.addEventListener('DOMContentLoaded', initStats);