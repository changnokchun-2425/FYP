"""
========================================
SAMPLE MOVIE DATA
========================================

Purpose: Store sample movie data for testing and development
Usage: Import this file to populate database with test data

Sections:
1. Now Showing Movies
2. Coming Soon Movies
3. Movie Genres
4. Helper Functions

========================================
"""

# ==========================================================
# SECTION 1: NOW SHOWING MOVIES
# Purpose: Sample data for currently showing movies
# ==========================================================

NOW_SHOWING_MOVIES = [
    {
        'title': '復仇者聯盟：終局之戰',
        'title_en': 'Avengers: Endgame',
        'duration': '181分鐘',
        'rating': 'IIB',
        'genre': '動作 / 科幻',
        'description': '在薩諾斯消滅了一半的宇宙生命後，復仇者聯盟必須集結起來，扭轉局勢並恢復宇宙的秩序。',
        'director': 'Anthony Russo, Joe Russo',
        'cast': 'Robert Downey Jr., Chris Evans, Mark Ruffalo',
        'language': '英語 (中文字幕)',
        'release_date': '2019-04-24',
        'price': 120.00,
        'poster': 'https://via.placeholder.com/300x450/1a1a1a/e50914?text=Avengers+Endgame',
        'trailer_url': 'https://www.youtube.com/watch?v=TcMBFSGVi1c',
        'status': 'now_showing'
    },
    {
        'title': '蜘蛛俠：不戰無歸',
        'title_en': 'Spider-Man: No Way Home',
        'duration': '148分鐘',
        'rating': 'IIA',
        'genre': '動作 / 冒險',
        'description': '彼得·帕克的身份被揭露後，他尋求奇異博士的幫助，但魔法失控打開了多重宇宙的大門。',
        'director': 'Jon Watts',
        'cast': 'Tom Holland, Zendaya, Benedict Cumberbatch',
        'language': '英語 (中文字幕)',
        'release_date': '2021-12-15',
        'price': 130.00,
        'poster': 'https://via.placeholder.com/300x450/1a1a1a/2a5298?text=Spider-Man',
        'trailer_url': 'https://www.youtube.com/watch?v=JfVOs4VSpmA',
        'status': 'now_showing'
    },
    {
        'title': '沙丘',
        'title_en': 'Dune',
        'duration': '155分鐘',
        'rating': 'IIA',
        'genre': '科幻 / 冒險',
        'description': '保羅·亞崔迪前往宇宙中最危險的星球，以確保他家族和人民的未來。',
        'director': 'Denis Villeneuve',
        'cast': 'Timothée Chalamet, Rebecca Ferguson, Zendaya',
        'language': '英語 (中文字幕)',
        'release_date': '2021-09-15',
        'price': 110.00,
        'poster': 'https://via.placeholder.com/300x450/1a1a1a/f39c12?text=Dune',
        'trailer_url': 'https://www.youtube.com/watch?v=8g18jFHCLXk',
        'status': 'now_showing'
    },
    {
        'title': '奧本海默',
        'title_en': 'Oppenheimer',
        'duration': '180分鐘',
        'rating': 'IIB',
        'genre': '傳記 / 劇情',
        'description': '羅伯特·奧本海默在二戰期間領導曼哈頓計劃，研發第一顆原子彈的故事。',
        'director': 'Christopher Nolan',
        'cast': 'Cillian Murphy, Emily Blunt, Matt Damon',
        'language': '英語 (中文字幕)',
        'release_date': '2023-07-21',
        'price': 140.00,
        'poster': 'https://via.placeholder.com/300x450/1a1a1a/e67e22?text=Oppenheimer',
        'trailer_url': 'https://www.youtube.com/watch?v=uYPbbksJxIg',
        'status': 'now_showing'
    },
    {
        'title': '芭比',
        'title_en': 'Barbie',
        'duration': '114分鐘',
        'rating': 'IIA',
        'genre': '喜劇 / 奇幻',
        'description': '芭比和肯尼離開完美的芭比樂園，前往現實世界展開冒險旅程。',
        'director': 'Greta Gerwig',
        'cast': 'Margot Robbie, Ryan Gosling, Will Ferrell',
        'language': '英語 (中文字幕)',
        'release_date': '2023-07-21',
        'price': 120.00,
        'poster': 'https://via.placeholder.com/300x450/1a1a1a/e91e63?text=Barbie',
        'trailer_url': 'https://www.youtube.com/watch?v=pBk4NYhWNMM',
        'status': 'now_showing'
    },
    {
        'title': '捍衛戰士：獨行俠',
        'title_en': 'Top Gun: Maverick',
        'duration': '131分鐘',
        'rating': 'IIA',
        'genre': '動作 / 劇情',
        'description': '皮特·米契爾回到精英飛行員學校，訓練新一代的頂尖飛行員執行危險任務。',
        'director': 'Joseph Kosinski',
        'cast': 'Tom Cruise, Miles Teller, Jennifer Connelly',
        'language': '英語 (中文字幕)',
        'release_date': '2022-05-27',
        'price': 130.00,
        'poster': 'https://via.placeholder.com/300x450/1a1a1a/3498db?text=Top+Gun',
        'trailer_url': 'https://www.youtube.com/watch?v=giXco2jaZ_4',
        'status': 'now_showing'
    }
]

# ==========================================================
# SECTION 2: COMING SOON MOVIES
# Purpose: Sample data for upcoming movies
# ==========================================================

COMING_SOON_MOVIES = [
    {
        'title': '沙丘：第二章',
        'title_en': 'Dune: Part Two',
        'duration': '166分鐘',
        'rating': 'IIA',
        'genre': '科幻 / 冒險',
        'description': '保羅與奇妮繼續在沙漠星球上的史詩冒險，面對更大的挑戰和陰謀。',
        'director': 'Denis Villeneuve',
        'cast': 'Timothée Chalamet, Zendaya, Austin Butler',
        'language': '英語 (中文字幕)',
        'release_date': '2024-03-01',
        'price': 140.00,
        'poster': 'https://via.placeholder.com/300x450/1a1a1a/9b59b6?text=Dune+Part+2',
        'trailer_url': 'https://www.youtube.com/watch?v=Way9Dexny3w',
        'status': 'coming_soon'
    },
    {
        'title': '死侍與金鋼狼',
        'title_en': 'Deadpool & Wolverine',
        'duration': '未定',
        'rating': 'IIB',
        'genre': '動作 / 喜劇',
        'description': '死侍與金鋼狼聯手，在多重宇宙中展開瘋狂冒險。',
        'director': 'Shawn Levy',
        'cast': 'Ryan Reynolds, Hugh Jackman',
        'language': '英語 (中文字幕)',
        'release_date': '2024-07-26',
        'price': 130.00,
        'poster': 'https://via.placeholder.com/300x450/1a1a1a/c0392b?text=Deadpool+3',
        'trailer_url': '',
        'status': 'coming_soon'
    },
    {
        'title': '銀河守護隊3',
        'title_en': 'Guardians of the Galaxy Vol. 3',
        'duration': '150分鐘',
        'rating': 'IIA',
        'genre': '動作 / 科幻',
        'description': '銀河守護隊展開新的任務，揭開火箭浣熊的神秘過去。',
        'director': 'James Gunn',
        'cast': 'Chris Pratt, Zoe Saldana, Dave Bautista',
        'language': '英語 (中文字幕)',
        'release_date': '2023-05-05',
        'price': 120.00,
        'poster': 'https://via.placeholder.com/300x450/1a1a1a/16a085?text=Guardians+3',
        'trailer_url': 'https://www.youtube.com/watch?v=u3V5KDHRQvk',
        'status': 'coming_soon'
    },
    {
        'title': '星際大戰：俠盜小隊',
        'title_en': 'Star Wars: Rogue Squadron',
        'duration': '未定',
        'rating': 'IIA',
        'genre': '科幻 / 冒險',
        'description': '星際大戰宇宙的新篇章，講述精英飛行員小隊的故事。',
        'director': 'Patty Jenkins',
        'cast': '未公布',
        'language': '英語 (中文字幕)',
        'release_date': '2025-12-18',
        'price': 150.00,
        'poster': 'https://via.placeholder.com/300x450/1a1a1a/2c3e50?text=Star+Wars',
        'trailer_url': '',
        'status': 'coming_soon'
    }
]

# ==========================================================
# SECTION 3: MOVIE GENRES
# Purpose: Standard genre categories
# ==========================================================

GENRES = [
    '動作',
    '冒險',
    '科幻',
    '劇情',
    '喜劇',
    '恐怖',
    '驚悚',
    '浪漫',
    '犯罪',
    '傳記',
    '奇幻',
    '動畫',
    '紀錄片',
    '音樂',
    '戰爭',
    '西部',
    '家庭',
    '懸疑'
]

# ==========================================================
# SECTION 4: RATING CATEGORIES
# Purpose: Hong Kong film rating system
# ==========================================================

RATINGS = {
    'I': '適合所有年齡人士觀看',
    'IIA': '兒童不宜',
    'IIB': '青少年及兒童不宜',
    'III': '只准18歲或以上人士觀看'
}

# ==========================================================
# SECTION 5: HELPER FUNCTIONS
# Purpose: Utility functions for movie data
# ==========================================================

def get_all_movies():
    """
    Get all movies (both now showing and coming soon)
    
    Returns:
        list: Combined list of all movies
    """
    return NOW_SHOWING_MOVIES + COMING_SOON_MOVIES


def get_movies_by_status(status):
    """
    Get movies filtered by status
    
    Args:
        status (str): 'now_showing' or 'coming_soon'
    
    Returns:
        list: Filtered movie list
    """
    all_movies = get_all_movies()
    return [movie for movie in all_movies if movie['status'] == status]


def get_movie_by_title(title):
    """
    Find a movie by its title
    
    Args:
        title (str): Movie title (Chinese or English)
    
    Returns:
        dict: Movie data or None if not found
    """
    all_movies = get_all_movies()
    for movie in all_movies:
        if movie['title'] == title or movie['title_en'] == title:
            return movie
    return None


def get_movies_by_genre(genre):
    """
    Get movies filtered by genre
    
    Args:
        genre (str): Genre name
    
    Returns:
        list: Movies matching the genre
    """
    all_movies = get_all_movies()
    return [movie for movie in all_movies if genre in movie['genre']]


def format_movie_for_display(movie):
    """
    Format movie data for template display
    
    Args:
        movie (dict): Movie data
    
    Returns:
        dict: Formatted movie data
    """
    return {
        **movie,
        'price_formatted': f"HK${movie['price']:.2f}",
        'genres_list': movie['genre'].split(' / '),
        'cast_list': movie['cast'].split(', ') if movie['cast'] != '未公布' else []
    }


# ==========================================================
# USAGE EXAMPLE
# ==========================================================

"""
# Import in your routes.py or create_db.py:

from app.data.sample_movies import (
    NOW_SHOWING_MOVIES,
    COMING_SOON_MOVIES,
    get_all_movies,
    get_movies_by_status
)

# Get now showing movies
now_showing = get_movies_by_status('now_showing')

# Get all movies
all_movies = get_all_movies()

# In your route:
@app.route('/cinema')
def cinema_index():
    movies = get_movies_by_status('now_showing')
    return render_template('cinema_index.html.j2', movies=movies)
"""
