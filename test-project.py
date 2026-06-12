# test_project.py
import pytest
from project import get_genre_list

def test_get_tmdb_token_missing(monkeypatch):
    """Test that the token function exits cleanly if the environment variable is missing."""
    import os
    monkeypatch.delenv("TMDB_READ_ACCESS_TOKEN", raising=False)
    
    with pytest.raises(SystemExit):
        from project import get_tmdb_token
        get_tmdb_token()

def test_genre_list_fallback():
    """Test that your genre handling doesn't crash given an invalid or empty token."""
    # Passing an empty string should safely return an empty dict or raise an exception
    # depending on your exact function design
    result = get_genre_list("")
    assert isinstance(result, dict)

def test_dataframe_structure():
    """Add a third test tailored to a helper function in your code."""
    # Replace this with a quick check on any helper function you wrote
    # e.g., checking if a URL string formatter returns a valid string
    assert True