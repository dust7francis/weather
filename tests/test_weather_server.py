"""Unit tests for weather_server.py module."""

import runpy
from typing import Any
from unittest.mock import MagicMock, patch

import requests

from weather_server import get_canberra_weather, get_weather, lookup_location, mcp

# --- Tests for lookup_location ---


def test_lookup_location_success_with_admin1() -> None:
    """Tests location lookup when admin1 (state/province) is present."""
    mock_payload: dict[str, Any] = {
        "results": [
            {
                "name": "Canberra",
                "country": "Australia",
                "admin1": "Australian Capital Territory",
                "latitude": -35.2835,
                "longitude": 149.1281,
            }
        ]
    }
    mock_response = MagicMock(spec=requests.Response)
    mock_response.json.return_value = mock_payload
    mock_response.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_response) as mock_get:
        result = lookup_location("Canberra")

        mock_get.assert_called_once_with(
            "https://geocoding-api.open-meteo.com/v1/search?name=Canberra&count=1&language=en"
        )
        assert (
            "📍 Found Location: Canberra, Australian Capital Territory, Australia"
            in result
        )
        assert "Latitude: -35.2835" in result
        assert "Longitude: 149.1281" in result


def test_lookup_location_success_without_admin1() -> None:
    """Tests location lookup when admin1 is omitted or empty."""
    mock_payload: dict[str, Any] = {
        "results": [
            {
                "name": "Singapore",
                "country": "Singapore",
                "admin1": "",
                "latitude": 1.3521,
                "longitude": 103.8198,
            }
        ]
    }
    mock_response = MagicMock(spec=requests.Response)
    mock_response.json.return_value = mock_payload
    mock_response.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_response):
        result = lookup_location("Singapore")

        assert "📍 Found Location: Singapore, Singapore" in result
        assert "Latitude: 1.3521" in result
        assert "Longitude: 103.8198" in result


def test_lookup_location_unknown_country() -> None:
    """Tests location lookup when country field is missing."""
    mock_payload: dict[str, Any] = {
        "results": [
            {
                "name": "Remote Island",
                "latitude": -10.0,
                "longitude": 100.0,
            }
        ]
    }
    mock_response = MagicMock(spec=requests.Response)
    mock_response.json.return_value = mock_payload
    mock_response.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_response):
        result = lookup_location("Remote Island")

        assert "📍 Found Location: Remote Island, Unknown Country" in result


def test_lookup_location_not_found() -> None:
    """Tests location lookup when no results match the query."""
    mock_response = MagicMock(spec=requests.Response)
    mock_response.json.return_value = {"results": []}
    mock_response.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_response):
        result = lookup_location("Atlantis")
        assert (
            "❌ Could not find any location coordinates matching 'Atlantis'." in result
        )


def test_lookup_location_request_exception() -> None:
    """Tests location lookup error handling on network exception."""
    with patch(
        "requests.get",
        side_effect=requests.exceptions.ConnectionError("DNS lookup failed"),
    ):
        result = lookup_location("Paris")
        assert "Error during location lookup for 'Paris': DNS lookup failed" in result


# --- Tests for get_weather ---


def test_get_weather_success() -> None:
    """Tests retrieving weather for a city successfully."""
    mock_geo_resp = MagicMock(spec=requests.Response)
    mock_geo_resp.json.return_value = {
        "results": [{"latitude": 35.6762, "longitude": 139.6503}]
    }
    mock_geo_resp.raise_for_status.return_value = None

    mock_weather_resp = MagicMock(spec=requests.Response)
    mock_weather_resp.json.return_value = {
        "current": {
            "time": "2026-09-27T15:00",
            "temperature_2m": 21.0,
            "wind_speed_10m": 8.0,
        }
    }
    mock_weather_resp.raise_for_status.return_value = None

    with patch(
        "requests.get", side_effect=[mock_geo_resp, mock_weather_resp]
    ) as mock_get:
        result = get_weather("Tokyo")

        assert mock_get.call_count == 2
        assert "name=Tokyo" in mock_get.call_args_list[0][0][0]
        assert "latitude=35.6762&longitude=139.6503" in mock_get.call_args_list[1][0][0]
        assert "🌍 Weather Report 🌍" in result
        assert "Time:    2026-09-27T15:00" in result
        assert "Temperature: 21.0°C" in result
        assert "Wind speed: 8.0km/h" in result


def test_get_weather_city_not_found() -> None:
    """Tests get_weather when city coordinates cannot be found."""
    mock_geo_resp = MagicMock(spec=requests.Response)
    mock_geo_resp.json.return_value = {"results": []}
    mock_geo_resp.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_geo_resp) as mock_get:
        result = get_weather("NonExistentPlace")

        assert mock_get.call_count == 1
        assert (
            "❌ Could not find any location coordinates matching 'NonExistentPlace'."
            in result
        )


def test_get_weather_geocoding_exception() -> None:
    """Tests get_weather handling network failure during geocoding step."""
    with patch(
        "requests.get",
        side_effect=requests.exceptions.ConnectionError("Geocoding connection timeout"),
    ):
        result = get_weather("Sydney")
        assert (
            "Error fetching weather data for coordinates (None, None) of city Sydney"
            in result
        )
        assert "Geocoding connection timeout" in result


def test_get_weather_forecast_exception() -> None:
    """Tests get_weather handling network failure during forecast step."""
    mock_geo_resp = MagicMock(spec=requests.Response)
    mock_geo_resp.json.return_value = {
        "results": [{"latitude": 51.5074, "longitude": -0.1278}]
    }
    mock_geo_resp.raise_for_status.return_value = None

    with patch(
        "requests.get",
        side_effect=[
            mock_geo_resp,
            requests.exceptions.HTTPError("500 Internal Server Error"),
        ],
    ):
        result = get_weather("London")
        assert (
            "Error fetching weather data for coordinates (51.5074, -0.1278) of city London"
            in result
        )
        assert "500 Internal Server Error" in result


# --- Tests for get_canberra_weather ---


def test_get_canberra_weather_success() -> None:
    """Tests retrieving Canberra weather successfully."""
    mock_resp = MagicMock(spec=requests.Response)
    mock_resp.json.return_value = {
        "current": {
            "time": "2026-09-27T18:00",
            "temperature_2m": 23.1,
            "wind_speed_10m": 12.0,
        }
    }
    mock_resp.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_resp) as mock_get:
        result = get_canberra_weather()

        mock_get.assert_called_once()
        called_url: str = mock_get.call_args[0][0]
        assert "latitude=-35.2835" in called_url
        assert "longitude=149.1281" in called_url
        assert "☀️ Canberra Current Weather ☀️" in result
        assert "Time:    2026-09-27T18:00" in result
        assert "Temperature: 23.1°C" in result
        assert "Wind speed: 12.0km/h" in result


def test_get_canberra_weather_exception() -> None:
    """Tests get_canberra_weather error handling on request failure."""
    with patch(
        "requests.get",
        side_effect=requests.exceptions.RequestException("Canberra service offline"),
    ):
        result = get_canberra_weather()
        assert "Error fetching weather data: Canberra service offline" in result


# --- Server and Main execution tests ---


def test_mcp_server_properties() -> None:
    """Tests FastMCP server instance configuration."""
    assert mcp.name == "Global Weather & Location Server"


def test_main_execution() -> None:
    """Tests executing weather_server as __main__ invokes mcp.run()."""
    with patch("mcp.server.mcpserver.MCPServer.run") as mock_run:
        runpy.run_module("weather_server", run_name="__main__")
        mock_run.assert_called_once()
