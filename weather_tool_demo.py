#!/usr/bin/env python3
"""Minimal chatbot demo for BrightPath EdTech.

The chatbot uses free open weather data from Open-Meteo so different Indian
cities return different forecasts without any paid API key.
"""

from __future__ import annotations

import json
import os
import re
from importlib import import_module
from functools import lru_cache
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen
from typing import Any

try:
    anthropic = import_module("anthropic")
except ImportError:  # pragma: no cover - optional dependency
    anthropic = None


def get_weather(city: str) -> str:
    """Fetch a forecast for an Indian city from Open-Meteo."""

    location = geocode_city_in_india(city)
    if location is None:
        return f"I could not find a forecast for {city.strip()}. Try another Indian city name."

    forecast = fetch_forecast(location["latitude"], location["longitude"], location["timezone"])
    return format_forecast(location, forecast)


def http_get_json(url: str) -> dict[str, Any]:
    with urlopen(url, timeout=20) as response:
        payload = response.read().decode("utf-8")
    return json.loads(payload)


@lru_cache(maxsize=256)
def geocode_city_in_india(city: str) -> dict[str, Any] | None:
    params = {
        "name": city.strip(),
        "count": 1,
        "language": "en",
        "format": "json",
        "countryCode": "IN",
    }
    url = "https://geocoding-api.open-meteo.com/v1/search?" + urlencode(params)
    try:
        data = http_get_json(url)
    except (HTTPError, URLError, TimeoutError, ValueError):
        return None

    results = data.get("results") or []
    if not results:
        return None
    return results[0]


def fetch_forecast(latitude: float, longitude: float, timezone: str) -> dict[str, Any]:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,precipitation_sum,wind_speed_10m_max",
        "timezone": timezone or "auto",
        "forecast_days": 1,
        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",
        "precipitation_unit": "mm",
        "timeformat": "iso8601",
    }
    url = "https://api.open-meteo.com/v1/forecast?" + urlencode(params)
    try:
        return http_get_json(url)
    except (HTTPError, URLError, TimeoutError, ValueError) as exc:
        return {"error": str(exc)}


def weather_code_description(code: int) -> str:
    descriptions = {
        0: "clear sky",
        1: "mainly clear",
        2: "partly cloudy",
        3: "overcast",
        45: "fog",
        48: "depositing rime fog",
        51: "light drizzle",
        53: "moderate drizzle",
        55: "dense drizzle",
        56: "light freezing drizzle",
        57: "dense freezing drizzle",
        61: "slight rain",
        63: "moderate rain",
        65: "heavy rain",
        66: "light freezing rain",
        67: "heavy freezing rain",
        71: "slight snow fall",
        73: "moderate snow fall",
        75: "heavy snow fall",
        80: "slight rain showers",
        81: "moderate rain showers",
        82: "violent rain showers",
        85: "slight snow showers",
        86: "heavy snow showers",
        95: "thunderstorm",
        96: "thunderstorm with hail",
        99: "thunderstorm with heavy hail",
    }
    return descriptions.get(code, f"weather code {code}")


def format_forecast(location: dict[str, Any], forecast: dict[str, Any]) -> str:
    if forecast.get("error"):
        return f"I found {location['name']}, but the weather service returned an error."

    daily = forecast.get("daily", {})
    if not daily:
        return f"I found {location['name']}, but no forecast data was returned."

    date = daily.get("time", ["today"])[0]
    tmax = daily.get("temperature_2m_max", [None])[0]
    tmin = daily.get("temperature_2m_min", [None])[0]
    precip_prob = daily.get("precipitation_probability_max", [None])[0]
    precip_sum = daily.get("precipitation_sum", [None])[0]
    wind = daily.get("wind_speed_10m_max", [None])[0]
    weather_code = daily.get("weather_code", [None])[0]

    parts = [f"Forecast for {location['name']}, India on {date}"]
    if tmin is not None and tmax is not None:
        parts.append(f"low {tmin:.0f}°C, high {tmax:.0f}°C")
    if weather_code is not None:
        parts.append(weather_code_description(int(weather_code)))
    if precip_prob is not None:
        parts.append(f"rain chance {precip_prob:.0f}%")
    if precip_sum is not None:
        parts.append(f"precipitation {precip_sum:.1f} mm")
    if wind is not None:
        parts.append(f"wind up to {wind:.0f} km/h")

    return parts[0] + (": " + ", ".join(parts[1:]) if len(parts) > 1 else "") + "."


def extract_city(question: str) -> str:
    """Pull a likely city name out of a weather question.

    This is only for the local demo path; Claude can infer the city itself in
    live mode.
    """

    patterns = [
        r"\bin ([a-zA-Z]+(?:\s+[a-zA-Z]+)*)\b",
        r"\bfor ([a-zA-Z]+(?:\s+[a-zA-Z]+)*)\b",
        r"\bat ([a-zA-Z]+(?:\s+[a-zA-Z]+)*)\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, question, flags=re.IGNORECASE)
        if match:
            return normalize_city_phrase(match.group(1))
    return "your city"


def normalize_city_phrase(text: str) -> str:
    words = text.strip(" ?!.,").split()
    trailing_words = {"today", "tomorrow", "tonight", "now", "please", "weather", "forecast"}
    while words and words[-1].lower() in trailing_words:
        words.pop()
    return " ".join(words) if words else text.strip(" ?!.,")


def looks_weather_related(question: str) -> bool:
    keywords = (
        "weather",
        "umbrella",
        "rain",
        "sunny",
        "forecast",
        "temperature",
        "hot",
        "cold",
        "humid",
        "cloudy",
        "sports class",
    )
    lowered = question.lower()
    return any(keyword in lowered for keyword in keywords)


def is_general_capital_question(question: str) -> bool:
    lowered = question.lower()
    return "capital of rajasthan" in lowered or lowered.strip() == "capital of rajasthan"


def run_local_demo(question: str) -> dict[str, Any]:
    """Simulate a Claude-style tool decision without any external API call."""

    result: dict[str, Any] = {"question": question}
    if looks_weather_related(question):
        city = extract_city(question)
        tool_output = get_weather(city)
        result["tool_called"] = True
        result["tool_name"] = "get_weather"
        result["tool_input"] = {"city": city}
        result["tool_output"] = tool_output
        result["answer"] = (
            f"You probably do not need an umbrella. {tool_output}"
        )
    else:
        result["tool_called"] = False
        if is_general_capital_question(question):
            result["answer"] = "The capital of Rajasthan is Jaipur."
        else:
            result["answer"] = (
                "I’m a simple demo chatbot. Ask me about weather or a basic "
                "general-knowledge question."
            )
    return result


def run_with_claude(
    question: str, history: list[dict[str, Any]] | None = None
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Use the Anthropic API with Claude's tool-use loop."""

    if anthropic is None:
        raise RuntimeError("anthropic package is not installed")

    messages: list[dict[str, Any]] = [] if history is None else list(history)
    client = anthropic.Anthropic()
    tool = {
        "name": "get_weather",
        "description": "Return a weather forecast for an Indian city using open data.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"}
            },
            "required": ["city"],
            "additionalProperties": False,
        },
    }

    system_prompt = (
        "You are a helpful assistant for a student asking about weather before "
        "sports class. Use the get_weather tool only when the user asks about "
        "weather, rain, umbrellas, temperature, or similar conditions. If the "
        "question is not weather-related, answer directly and do not call the "
        "tool."
    )

    first_response = client.messages.create(
        model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
        max_tokens=300,
        system=system_prompt,
        tools=[tool],
        tool_choice="auto",
        messages=messages + [{"role": "user", "content": question}],
    )

    tool_use_block = next(
        (block for block in first_response.content if block.type == "tool_use"),
        None,
    )

    if tool_use_block is None:
        final_text = "".join(
            block.text for block in first_response.content if block.type == "text"
        ).strip()
        result = {
            "question": question,
            "tool_called": False,
            "answer": final_text,
        }
        messages.extend(
            [
                {"role": "user", "content": question},
                {"role": "assistant", "content": first_response.content},
            ]
        )
        return result, messages

    tool_input = tool_use_block.input
    tool_output = get_weather(tool_input["city"])

    second_response = client.messages.create(
        model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
        max_tokens=300,
        system=system_prompt,
        tools=[tool],
        messages=[
            {"role": "user", "content": question},
            {"role": "assistant", "content": first_response.content},
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use_block.id,
                        "content": tool_output,
                    }
                ],
            },
        ],
    )

    final_text = "".join(
        block.text for block in second_response.content if block.type == "text"
    ).strip()
    result = {
        "question": question,
        "tool_called": True,
        "tool_name": tool_use_block.name,
        "tool_input": tool_input,
        "tool_output": tool_output,
        "answer": final_text,
    }
    messages.extend(
        [
            {"role": "user", "content": question},
            {"role": "assistant", "content": first_response.content},
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use_block.id,
                        "content": tool_output,
                    }
                ],
            },
            {"role": "assistant", "content": second_response.content},
        ]
    )
    return result, messages


def answer_question(question: str) -> dict[str, Any]:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key and anthropic is not None:
        try:
            result, _ = run_with_claude(question)
            return result
        except Exception:
            pass
    return run_local_demo(question)


def print_result(question: str, result: dict[str, Any]) -> None:
    print(f"Question: {question}")
    if result["tool_called"]:
        print(
            f"Tool call: {result['tool_name']}({json.dumps(result['tool_input'])})"
        )
        print(f"Tool output: {result['tool_output']}")
    else:
        print("Tool call: none")
    print(f"Final answer: {result['answer']}")
    print()


def chat() -> None:
    print("BrightPath chatbot")
    print("Type a question and press Enter. Type 'reset' to clear history or 'quit' to exit.")
    print()

    history: list[dict[str, Any]] = []

    while True:
        try:
            question = input("You: ").strip()
        except EOFError:
            print()
            break

        if not question:
            continue

        lowered = question.lower()
        if lowered in {"quit", "exit"}:
            print("Bot: Goodbye.")
            break
        if lowered == "reset":
            history.clear()
            print("Bot: Conversation reset.")
            continue

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key and anthropic is not None:
            try:
                result, history = run_with_claude(question, history)
            except Exception:
                result = run_local_demo(question)
        else:
            result = run_local_demo(question)

        print_result(question, result)


def main() -> None:
    chat()


if __name__ == "__main__":
    main()