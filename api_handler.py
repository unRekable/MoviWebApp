import os
import requests
import dotenv

# Load environment variables from the .env file
dotenv.load_dotenv()

API_KEY = os.getenv("API_KEY")
API_URL = os.getenv("API_URL")

class MovieAPIError(Exception):
    """Exception raised for specific errors returned by the movie API."""
    pass

def get_movie_by_title(title: str) -> dict | None:
    """
    Fetches movie data from the OMDb API by title.

    Args:
        title: The title of the movie to search for.

    Returns:
        A dictionary containing movie data if found, None if the movie is not found
        or the title is empty.

    Raises:
        MovieAPIError: If the API returns an error other than "Movie not found!"
                       (e.g., invalid API key, request limit exceeded).
        requests.exceptions.RequestException: For any network-related issues
                                              (e.g., connection error, timeout, HTTP errors).
    """
    if not title:
        return None

    if not API_KEY or not API_URL:
        raise MovieAPIError("API_KEY or API_URL environment variables are not set.")

    try:
        params = {
            "apikey": API_KEY,
            "t": title
        }
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()

        result = response.json()

        if result.get("Response") == "False":
            error_message = result.get("Error", "Unknown API error")
            if error_message == "Movie not found!":
                return None
            else:
                raise MovieAPIError(error_message)

        return result

    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"Network or HTTP error during API call: {e}") from e
