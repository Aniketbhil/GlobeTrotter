import csv
from pathlib import Path

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.features.activities.models import Activity, ActivityType
from app.features.cities.models import City


def seed(db: Session | None = None):
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        cities_path = Path("seed_data/cities.csv")
        activities_path = Path("seed_data/activities.csv")

        if not cities_path.exists() or not activities_path.exists():
            print("Seed files missing in seed_data/")
            return

        cities_inserted = 0
        cities_updated = 0

        with open(cities_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row["name"].strip()
                country = row["country"].strip()
                region = row["region"].strip() if row.get("region") else None
                cost_index = float(row["cost_index"]) if row.get("cost_index") else None
                popularity_score = (
                    int(row["popularity_score"]) if row.get("popularity_score") else 0
                )
                image_url = row["image_url"].strip() if row.get("image_url") else None

                existing = (
                    db.query(City)
                    .filter(
                        func.lower(City.name) == name.lower(),
                        func.lower(City.country) == country.lower(),
                    )
                    .first()
                )

                if existing:
                    existing.region = region
                    existing.cost_index = cost_index
                    existing.popularity_score = popularity_score
                    if image_url:
                        existing.image_url = image_url
                    cities_updated += 1
                else:
                    new_city = City(
                        name=name,
                        country=country,
                        region=region,
                        cost_index=cost_index,
                        popularity_score=popularity_score,
                        image_url=image_url,
                    )
                    db.add(new_city)
                    cities_inserted += 1

        db.commit()

        activities_inserted = 0
        activities_updated = 0
        activities_skipped = 0

        with open(activities_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                city_name = row["city_name"].strip()
                city_country = row["city_country"].strip()
                act_name = row["name"].strip()
                raw_type = row["type"].strip().lower()
                cost = float(row["cost"]) if row.get("cost") else 0.0
                duration_mins = (
                    int(row["duration_mins"]) if row.get("duration_mins") else None
                )
                description = (
                    row["description"].strip() if row.get("description") else None
                )
                image_url = row["image_url"].strip() if row.get("image_url") else None

                city = (
                    db.query(City)
                    .filter(
                        func.lower(City.name) == city_name.lower(),
                        func.lower(City.country) == city_country.lower(),
                    )
                    .first()
                )

                if not city:
                    print(
                        f"WARNING: City '{city_name}, {city_country}' not found"
                        f" for activity '{act_name}'. Skipping."
                    )
                    activities_skipped += 1
                    continue

                try:
                    act_type = ActivityType(raw_type)
                except ValueError:
                    print(
                        f"WARNING: Invalid activity type '{raw_type}' for"
                        f" '{act_name}'. Skipping."
                    )
                    activities_skipped += 1
                    continue

                existing_act = (
                    db.query(Activity)
                    .filter(
                        Activity.city_id == city.id,
                        func.lower(Activity.name) == act_name.lower(),
                    )
                    .first()
                )

                if existing_act:
                    existing_act.type = act_type
                    existing_act.cost = cost
                    existing_act.duration_mins = duration_mins
                    existing_act.description = description
                    if image_url:
                        existing_act.image_url = image_url
                    activities_updated += 1
                else:
                    new_act = Activity(
                        city_id=city.id,
                        name=act_name,
                        type=act_type,
                        cost=cost,
                        duration_mins=duration_mins,
                        description=description,
                        image_url=image_url,
                    )
                    db.add(new_act)
                    activities_inserted += 1

        db.commit()

        print(f"Cities: {cities_inserted} inserted, {cities_updated} updated")
        print(
            f"Activities: {activities_inserted} inserted,"
            f" {activities_updated} updated, {activities_skipped} skipped"
        )
    finally:
        if close_db:
            db.close()


if __name__ == "__main__":
    seed()
