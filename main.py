import requests
from collections import Counter
from reactpy import component, html, hooks, run

cdn_1 = html.link(
    {
        "href": "https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css",
        "rel": "stylesheet",
    }
)

# Función de recomendación
def recomendar_animes(usuario):
    if not usuario.strip():  # Verificar que el usuario no esté vacío
        return ["Por favor, ingresa un nombre de usuario válido."]
    
    try:
        # Obtener animes populares
        response_animes = requests.get("https://api.jikan.moe/v4/top/anime")
        if response_animes.status_code != 200:
            return ["Error al obtener animes populares."]
        animes = response_animes.json()

        # Obtener datos del usuario desde la API
        response_user = requests.get(f"https://api.jikan.moe/v4/users/{usuario}/full")
        if response_user.status_code != 200:
            return [f"Error al obtener datos del usuario '{usuario}'."]

        # Obtener favoritos del usuario
        favorites_url = f"https://api.jikan.moe/v4/users/{usuario}/favorites"
        response_favorites = requests.get(favorites_url)
        if response_favorites.status_code != 200:
            return [f"Error al obtener los favoritos del usuario '{usuario}'."]
        favorites = response_favorites.json()
        favorite_ids = [fav['mal_id'] for fav in favorites['data']['anime']]

        # Buscar géneros de los favoritos del usuario
        user_genres = []
        for fav_id in favorite_ids:
            anime_url = f"https://api.jikan.moe/v4/anime/{fav_id}"
            response_anime = requests.get(anime_url)
            if response_anime.status_code == 200:
                anime_data = response_anime.json()
                genres = anime_data['data'].get('genres', [])
                user_genres.extend([genre['name'] for genre in genres])

        # Calcular géneros más comunes
        genre_counts = Counter(user_genres)
        max_frequency = max(genre_counts.values()) if genre_counts else 0
        relative_threshold = max(1, int(max_frequency * 0.6))
        filtered_genres = [genre for genre, count in genre_counts.items() if count >= relative_threshold]

        # Buscar animes populares con géneros comunes
        recommended_animes = []
        for popular_anime in animes['data']:
            anime_genres = [genre['name'] for genre in popular_anime.get('genres', [])]
            if any(genre in filtered_genres for genre in anime_genres):
                recommended_animes.append(popular_anime['title'])

        return recommended_animes if recommended_animes else ["No se encontraron recomendaciones."]
    except Exception as e:
        return [f"Error inesperado: {str(e)}"]

# Componente principal
@component
def App():
    usuario, set_usuario = hooks.use_state("")  # Estado para el nombre de usuario
    recomendaciones, set_recomendaciones = hooks.use_state([])  # Estado para las recomendaciones

    def obtener_recomendaciones(event=None):
        # Validar usuario antes de llamar a la función
        if usuario.strip():
            resultado = recomendar_animes(usuario)
            set_recomendaciones(resultado)
        else:
            set_recomendaciones(["Por favor, ingresa un nombre de usuario válido."])

    return html.div(
        {
            "className":"w-full h-full bg-black"
        },

        cdn_1,
        html.div(
            {
                "className":""
            },
             html.h1({"className":"text-3xl text-white font-bold"},"Recomendador de Anime"),
            html.label({"className":"text-white font-bold"},"Nombre de Usuario: "),
            html.input(
                {
                    "className":"text-white",
                    "type": "text",
                    "value": usuario,
                    "on_change": lambda event: set_usuario(event["target"]["value"]),
                }
            ),
            html.button(
                {
                    "on_click": obtener_recomendaciones,
                    "className":"bg-white text-black mx-5"
                 },
                "Obtener Recomendaciones",
            ),
        ),
        html.h2({"className":"text-white"},"Recomendaciones:"),
        html.ul([html.li({"className":"text-white"},anime) for anime in recomendaciones])
    )

# Ejecutar la aplicación
run(App)
