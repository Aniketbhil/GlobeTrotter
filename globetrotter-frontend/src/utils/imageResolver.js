// Hardcoded beautiful Unsplash URLs for the exact 25 seeded cities
const CITY_IMAGES = {
  'Paris': 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800&q=80',
  'Tokyo': 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800&q=80',
  'New York': 'https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=800&q=80',
  'Rome': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTTb6v7Yf9Wmc4E-BBuewdDbKDSdNEmYHI6B2iP1bXrrSmkREkEkqF5tdRP&s=10',
  'Barcelona': 'https://images.unsplash.com/photo-1583422409516-2895a77efded?w=800&q=80',
  'London': 'https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=800&q=80',
  'Bangkok': 'https://images.unsplash.com/photo-1582468546235-9bf31e5bc4a1?w=800&q=80',
  'Dubai': 'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=800&q=80',
  'Singapore': 'https://images.unsplash.com/photo-1525625293386-3f8f99389edd?w=800&q=80',
  'Sydney': 'https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?w=800&q=80',
  'Cape Town': 'https://images.unsplash.com/photo-1580060839134-75a5edca2e99?w=800&q=80',
  'Rio de Janeiro': 'https://images.unsplash.com/photo-1483729558449-99ef09a8c325?w=800&q=80',
  'Amsterdam': 'https://images.unsplash.com/photo-1512470876302-972faa2aa9a4?w=800&q=80',
  'Istanbul': 'https://images.unsplash.com/photo-1541432901042-2d8bd64b4a9b?w=800&q=80',
  'Denpasar': 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=800&q=80',
  'Kyoto': 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=800&q=80',
  'Prague': 'https://images.unsplash.com/photo-1519677100203-a0e668c92439?w=800&q=80',
  'Marrakech': 'https://images.unsplash.com/photo-1539020140153-e479b8c22e70?w=800&q=80',
  'Reykjavik': 'https://images.unsplash.com/photo-1516834474-48c0abc2a902?w=800&q=80',
  'Vancouver': 'https://images.unsplash.com/photo-1559511260-66a654ae982a?w=800&q=80',
  'Buenos Aires': 'https://images.unsplash.com/photo-1613243555988-441166d4d6fd?w=800&q=80',
  'Cairo': 'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=800&q=80',
  'Seoul': 'https://images.unsplash.com/photo-1538485399081-7191377e8241?w=800&q=80',
  'Lisbon': 'https://images.unsplash.com/photo-1587222318667-31212ce2828d?w=800&q=80',
  'Santorini': 'https://images.unsplash.com/photo-1613395877344-13d4a8e0d49e?w=800&q=80'
};

const DEFAULT_CITY = 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800&q=80';

// Keywords based on the seed data activities
const ACTIVITY_KEYWORDS = [
  { keywords: ['cruise', 'boat', 'sailing'], img: 'https://images.unsplash.com/photo-1548574505-12caf0050b5b?w=800&q=80' },
  { keywords: ['museum', 'gallery', 'louvre', 'art'], img: 'https://images.unsplash.com/photo-1583422409516-2895a77efded?w=800&q=80' },
  { keywords: ['market', 'bazaar'], img: 'https://images.unsplash.com/photo-1533900298318-6b8da08a523e?w=800&q=80' },
  { keywords: ['food', 'dinner', 'tasting', 'bbq', 'steakhouse', 'cooking', 'tapas'], img: 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800&q=80' },
  { keywords: ['bike', 'cycling'], img: 'https://images.unsplash.com/photo-1471506480208-91b3a4cc78be?w=800&q=80' },
  { keywords: ['trek', 'climb', 'safari', 'mountain'], img: 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800&q=80' },
  { keywords: ['spa', 'lagoon'], img: 'https://images.unsplash.com/photo-1544161515-4ab6ce6db874?w=800&q=80' },
  { keywords: ['show', 'theatre', 'broadway', 'cabaret'], img: 'https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=800&q=80' },
  { keywords: ['temple', 'shrine', 'mosque', 'cathedral'], img: 'https://images.unsplash.com/photo-1545562083-a600704fa486?w=800&q=80' }
];

const TYPE_FALLBACKS = {
  sightseeing: 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=800&q=80',
  food: 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800&q=80',
  adventure: 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800&q=80',
  culture: 'https://images.unsplash.com/photo-1583422409516-2895a77efded?w=800&q=80',
  nightlife: 'https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=800&q=80',
  other: DEFAULT_CITY
};

export const getCityImage = (cityName, customUrl = null) => {
  if (customUrl) return customUrl;
  if (!cityName) return DEFAULT_CITY;

  // Find key that matches city name (case insensitive)
  const match = Object.keys(CITY_IMAGES).find(k => k.toLowerCase() === cityName.toLowerCase());
  return match ? CITY_IMAGES[match] : DEFAULT_CITY;
};

export const getActivityImage = (activityName, type, customUrl = null) => {
  if (customUrl) return customUrl;

  if (activityName) {
    const nameLower = activityName.toLowerCase();
    for (const mapping of ACTIVITY_KEYWORDS) {
      if (mapping.keywords.some(kw => nameLower.includes(kw))) {
        return mapping.img;
      }
    }
  }
  return TYPE_FALLBACKS[type?.toLowerCase()] || DEFAULT_CITY;
};

export const getTripCoverImage = (tripName, customCoverUrl = null) => {
  if (customCoverUrl) return customCoverUrl;
  if (!tripName) return DEFAULT_CITY;

  const nameLower = tripName.toLowerCase();
  const match = Object.keys(CITY_IMAGES).find(k => nameLower.includes(k.toLowerCase()));
  if (match) return CITY_IMAGES[match];

  if (nameLower.includes('europe')) return CITY_IMAGES['Paris'];
  if (nameLower.includes('asia')) return CITY_IMAGES['Tokyo'];

  return DEFAULT_CITY;
};
