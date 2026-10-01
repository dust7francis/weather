"""Unit tests for weather_7days.py module."""

import runpy
from datetime import datetime
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import requests

from weather_7days import get_weather_7days


@pytest.fixture
def mock_7day_payload() -> dict[str, Any]:
    """Provides a sample Open-Meteo 7-day forecast API response payload."""
    return {
        "latitude": -35.2835,
        "longitude": 149.1281,
        "daily": {
            "time": [
                "2026-09-28",
                "2026-09-29",
                "2026-09-30",
                "2026-10-01",
                "2026-10-02",
                "2026-10-03",
                "2026-10-04",
            ],
            "temperature_2m_max": [19.8, 18.5, 21.7, 25.3, 27.1, 22.0, 20.5],
            "temperature_2m_min": [7.5, 6.9, 10.2, 11.4, 12.0, 9.8, 8.1],
            "precipitation_probability_max": [30, 40, 20, 10, 10, 50, 60],
        },
    }


def test_get_weather_7days_success(
    mock_7day_payload: dict[str, Any], capsys: pytest.CaptureFixture[str]
) -> None:
    """Tests successful 7-day forecast retrieval and tabular stdout formatting."""
    mock_response = MagicMock(spec=requests.Response)
    mock_response.json.return_value = mock_7day_payload
    mock_response.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_response) as mock_get:
        get_weather_7days()

        # Verify API call parameters
        mock_get.assert_called_once()
        called_url: str = mock_get.call_args[0][0]
        assert "latitude=-35.2835" in called_url
        assert "longitude=149.1281" in called_url
        assert "forecast_days=7" in called_url
        assert "timezone=Australia%2FSydney" in called_url
        assert (
            "daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max"
            in called_url
        )

        mock_response.raise_for_status.assert_called_once()
        mock_response.json.assert_called_once()

    captured = capsys.readouterr()
    assert "☀️ Canberra 7-day Weather Forecast ☀️" in captured.out
    assert "Date        Day         Min     Max     Rain" in captured.out

    # Verify each day's row
    daily = mock_7day_payload["daily"]
    for date, min_temp, max_temp, rain in zip(
        daily["time"],
        daily["temperature_2m_max"],
        daily["temperature_2m_min"],
        daily["precipitation_probability_max"],
    ):
        day_name = datetime.strptime(date, "%Y-%m-%d").strftime("%A")
        assert date in captured.out
        assert day_name in captured.out


def test_get_weather_7days_http_error(capsys: pytest.CaptureFixture[str]) -> None:
    """Tests handling of non-200 HTTP response codes."""
    mock_response = MagicMock(spec=requests.Response)
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "502 Bad Gateway"
    )

    with patch("requests.get", return_value=mock_response):
        get_weather_7days()

    captured = capsys.readouterr()
    assert "Error fetching weather data: 502 Bad Gateway" in captured.out


def test_get_weather_7days_connection_error(capsys: pytest.CaptureFixture[str]) -> None:
    """Tests handling of network connection failures."""
    with patch(
        "requests.get",
        side_effect=requests.exceptions.ConnectionError("Connection aborted"),
    ):
        get_weather_7days()

    captured = capsys.readouterr()
    assert "Error fetching weather data: Connection aborted" in captured.out


def test_get_weather_7days_timeout(capsys: pytest.CaptureFixture[str]) -> None:
    """Tests handling of request timeouts."""
    with patch(
        "requests.get",
        side_effect=requests.exceptions.Timeout("Read timeout"),
    ):
        get_weather_7days()

    captured = capsys.readouterr()
    assert "Error fetching weather data: Read timeout" in captured.out


def test_get_weather_7days_request_exception(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Tests handling of general RequestException."""
    with patch(
        "requests.get",
        side_effect=requests.exceptions.RequestException("Request failed"),
    ):
        get_weather_7days()

    captured = capsys.readouterr()
    assert "Error fetching weather data: Request failed" in captured.out


def test_main_execution(
    mock_7day_payload: dict[str, Any], capsys: pytest.CaptureFixture[str]
) -> None:
    """Tests execution of the script as __main__."""
    mock_response = MagicMock(spec=requests.Response)
    mock_response.json.return_value = mock_7day_payload
    mock_response.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_response):
        runpy.run_module("weather_7days", run_name="__main__")

    captured = capsys.readouterr()
    assert "☀️ Canberra 7-day Weather Forecast ☀️" in captured.out
    assert "2026-09-28" in captured.out
