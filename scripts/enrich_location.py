import json
import os
from pathlib import Path
from typing import Literal

import requests
from dotenv import load_dotenv
from jinja2 import Template
from openai import OpenAI
from pydantic import BaseModel, Field
from tqdm import tqdm

load_dotenv(dotenv_path="notebooks/.env")

API_BASE = "https://api.dugaapp.ru/api/v1"
PROXY_OPENAI_API = os.getenv("PROXY_OPENAI_API")
client = OpenAI(api_key=PROXY_OPENAI_API, base_url="https://api.proxyapi.ru/openai/v1")


CATEGORIES = (
    "Ресторан",
    "Кафе",
    "Бар",
    "Клуб",
    "Бильярдная",
    "Музей",
    "Книжный",
    "Парикмахерская",
    "Декор",
    "Блошиный рынок",
    "Магазин одежды",
    "Секонд-хенд",
    "Выставка",
    "Кинотеатр",
    "Мастерская",
    "Цветочный",
    "Театр",
    "Фотостудия",
    "Фотобудка",
    "Растяжка",
    "Йога",
    "Пилатес",
    "Спортивный клуб",
    "Спортивные коммьюнити",
    "Фестивали",
    "Загородный отель",
    "эко-отель",
)

TAGS = (
    "Шопинг",
    "За подарком",
    "На свидание",
    "Поработать",
    "Вдохновиться",
    "Узнать новое",
    "Рады мокрому носу",
    "Сжечь джоули",
    "Fancy",
    "Легкий андерграунд",
    "Выпить",
    "кусочек Питера",
    "Заземлиться",
    "На вечеринку",
)


class Tag(BaseModel):
    name: Literal[TAGS]  # type: ignore
    reason: str = Field(..., description="Объяснение, почему выбран этот тег")


class Category(BaseModel):
    name: Literal[CATEGORIES]  # type: ignore
    reason: str = Field(..., description="Объяснение, почему выбран эта категория")


class DescriptionFeedback(BaseModel):
    is_correct: bool
    feedback: None | str


class ChainOfThought(BaseModel):
    step_1_first_impression: str = Field(
        ..., description="Что первое бросается в глаза в локации или ощущается при описании"
    )
    step_2_what_is_unusual: str = Field(
        ..., description="Что необычного и почему об этом месте хочется рассказать другу"
    )
    step_3_usage_scenario: str = Field(
        ..., description="Сценарий: как человек может использовать это место (через 1–2 жизненных сцены)"
    )
    step_4_what_to_avoid: str = Field(
        ..., description="Что не стоит писать, чтобы избежать штампов, рекламных оборотов, лишней тяжеловесности"
    )
    theses: list[str] = Field(
        ...,
        description=(
            "3–5 черновых тезисов — короткие идеи, сцены или образы, расположенные в логической последовательности "
            "(от впечатления до сценария использования). Лягут в основу финального описания, пишутся в духе инструкции."
        ),
    )
    draft_description: str = Field(
        ...,
        description=(
            "Емкое описание локации (до 500 знаков), написанное на основе chain_of_thought, всех черновых тезисов "
            "(theses), строго в соответствии с предоставленной редакционной инструкцией."
        ),
    )


class LocationEnhancement(BaseModel):
    chain_of_thought: ChainOfThought
    generated_description: str = Field(
        ...,
        description=(
            "Финальное ёмкое описание локации (до 500 знаков), составленное на основе чернового описания "
            "(draft_description), строго в соответствии с предоставленной редакционной инструкцией. Если в "
            "draft_description есть ошибки или несоответствия гайду — исправь их, чтобы они не попали в финальный текст"
        ),
    )
    tags: list[Tag]
    categories: list[Category]
    # generated_description_is_correct: DescriptionFeedback
    # rewritten_generated_description: None | str


# ==== Функция генерации через LLM ====
def enhance_location(
    name: str, description: str, features: list[str], categories: list[str], working_hours: dict
) -> LocationEnhancement:
    with open("notebooks/prompt.txt", encoding="utf-8") as f:
        template = Template(f.read())

    prompt = template.render(
        name=name, description=description, features=features, categories=categories, working_hours=working_hours
    )

    response = client.responses.parse(
        model="gpt-4.1",
        temperature=0.6,
        input=[
            {"role": "user", "content": prompt},
        ],
        text_format=LocationEnhancement,
    )
    return response.output_parsed


# ==== Загрузка исходного JSON ====
def load_locations(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ==== Сохранение обратно в JSON ====
def save_locations(locations: list[dict], output_path: str) -> None:
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(locations, f, ensure_ascii=False, indent=2)


def enrich_locations(input_path: str, output_path: str) -> None:
    """Обогащает данные описанием, категориями и тегами с помощью LLM и сохраняет в новый JSON."""
    locations = load_locations(input_path)

    for loc in tqdm(locations, desc="Enrichment"):
        try:
            result = enhance_location(
                loc["name"], loc["description"], loc["features"], loc["categories"], loc["working_hours"]
            )
            loc["chain_of_thought"] = result.chain_of_thought.model_dump()
            loc["generated_description"] = result.generated_description
            loc["tags"] = [tag.model_dump() for tag in result.tags]
            loc["categories"] = [category.model_dump() for category in result.categories]
        except Exception as e:
            print(f"❌ Ошибка генерации для '{loc['name']}': {e}")
            loc["tags"] = []
            loc["categories"] = []

    save_locations(locations=locations, output_path=output_path)
    print(f"✅ Обогащённые данные сохранены в {output_path}")


def format_working_hours(working_hours: dict) -> str:
    """Преобразует словарь с рабочими часами в строку.
    Строка вида "Пн-Пт: 10:00-22:00, Сб-Вс: 11:00-23:00"
    """
    if not working_hours:
        return ""

    # Словарь для сокращения дней недели
    day_abbr = {
        "Понедельник": "Пн",
        "Вторник": "Вт",
        "Среда": "Ср",
        "Четверг": "Чт",
        "Пятница": "Пт",
        "Суббота": "Сб",
        "Воскресенье": "Вс",
    }

    # Группируем дни с одинаковым временем
    time_groups = {}
    for day, hours in working_hours.items():
        if hours not in time_groups:
            time_groups[hours] = []
        time_groups[hours].append(day_abbr[day])

    # Формируем строку
    result = []
    for hours, days in time_groups.items():
        if len(days) == 1:
            result.append(f"{days[0]}: {hours}")
        else:
            result.append(f"{days[0]}-{days[-1]}: {hours}")

    return ", ".join(result)


def create_location(item: dict) -> str:
    payload = {
        "name": item["name"],
        "latitude": item["coordinates"]["latitude"],
        "longitude": item["coordinates"]["longitude"],
        "categories": [category["name"] for category in item["categories"]],
        "tags": [tag["name"] for tag in item["tags"]],
        "instagram_url": None,
        "working_hours": format_working_hours(item.get("working_hours", {})),
        "address": item.get("address"),
        "description": item.get("generated_description"),
        "rating": float(item["rating"].replace(",", ".")) if item.get("rating") else None,
        "maps_url": item.get("link"),
    }
    resp = requests.post(f"{API_BASE}/locations", json=payload)
    resp.raise_for_status()
    return resp.json()["id"]


def upload_photos(location_id: str, photo_paths: list[str]) -> None:
    """Загружает фотографии для локации.

    Args:
        location_id: ID локации в API
        photo_paths: Список путей к фотографиям относительно notebooks/data/photos/
    """
    uploaded_count = 0
    for photo_path in photo_paths:
        full_path = f"notebooks/{photo_path}"
        if not os.path.exists(full_path):
            print(f"⚠️ Файл не найден: {full_path}")
            continue

        try:
            with open(full_path, "rb") as f:
                file_content = f.read()
                files = [("photos", (Path(photo_path).name, file_content, "image/jpeg"))]

                resp = requests.post(f"{API_BASE}/locations/{location_id}/photos", files=files)
                resp.raise_for_status()
                uploaded_count += 1
                print(f"✅ Загружено фото {uploaded_count}/{len(photo_paths)} для локации {location_id}")
        except Exception as e:
            print(f"❌ Ошибка при загрузке фото {full_path} для локации {location_id}: {e}")
            continue

    if uploaded_count == 0:
        print(f"⚠️ Не удалось загрузить ни одной фотографии для локации {location_id}")
    else:
        print(f"✅ Всего загружено {uploaded_count} фото для локации {location_id}")


def upload_to_api(json_path: str) -> None:
    """Загружает обогащённые локации в backend API."""
    locations = load_locations(json_path)[1:]

    for loc in tqdm(locations, desc="Uploading to API"):
        try:
            location_id = create_location(loc)
        except Exception as e:
            print(f"❌ Ошибка добавления '{loc['name']}' в API: {e}")
            continue

        try:
            upload_photos(location_id, loc.get("photo_paths", []))
        except Exception as e:
            print(f"⚠️ Ошибка загрузки фото для '{loc['name']}' ({location_id}): {e}")
            continue


if __name__ == "__main__":
    # enrich_locations(input_path="notebooks/data/locations.json", output_path="notebooks/data/locations_enriched.json")
    upload_to_api("notebooks/data/locations_enriched.json")
    # locations = load_locations("notebooks/data/locations.json")
    # for loc in locations:
    #     if not loc["description"]:
    #         print(json.dumps(loc, indent=4, ensure_ascii=False))
    #         result = enhance_location(
    #             loc["name"],
    #             loc["description"],
    #             loc["features"],
    #             loc["categories"],
    #             loc["working_hours"],
    #         )
    #         print(result)
    #         break
