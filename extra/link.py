from fastapi import FastAPI, HTTPException
import httpx
from bs4 import BeautifulSoup
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
import logging
from urllib.parse import urlparse

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Настройка подключения к MongoDB
MONGO_URI = "mongodb://localhost:27017"  # Замените на ваш URI
client = AsyncIOMotorClient(MONGO_URI)
db = client["webwellness_db"]
collection = db["reports"]

# Модель для валидации данных
class Report(BaseModel):
    test_id: str
    data: dict

# Функция для извлечения данных с URL
async def fetch_report(url: str) -> dict:
    # Валидация домена URL
    parsed_url = urlparse(url)
    if parsed_url.netloc != "profi.webwellness.bz":
        logger.error(f"Invalid URL domain: {parsed_url.netloc}")
        raise HTTPException(status_code=400, detail="Invalid URL domain")

    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            # Используем HTTPS
            url = url.replace("http://", "https://")
            logger.info(f"Fetching URL: {url}")
            response = await client.get(url, timeout=15.0)
            response.raise_for_status()

            # Парсинг HTML
            soup = BeautifulSoup(response.text, "html.parser")

            # Инициализация структуры данных
            test_id = url.split("testId=")[1].split("&")[0]
            data = {
                "test_id": test_id,
                "report": {
                    "general_state": {},
                    "diagram": {},
                    "spine": {},
                    "pathogens": [],
                    "changes": [],
                    "bio_age": {},
                    "vitamins": [],
                    "toxins": [],
                    "amino_acids": [],
                    "psychosomatics": [],
                    "reactivity": [],
                    "zodiac_diet": {},
                    "water_balance": {},
                    "energy_system": {},
                    "auragram": {},
                    "dynamics": {},
                    "ranking": {},
                    "imbalance_system": {}
                }
            }

            # Извлечение метаданных (Ф.И.О, сеанс, пол)
            metadata_div = soup.find("div", class_="report-metadata")  # Замените на реальный класс
            if metadata_div:
                logger.info("Found metadata section")
                data["report"]["general_state"]["metadata"] = {
                    "full_name": metadata_div.find("span", class_="full-name").text.strip() if metadata_div.find("span", class_="full-name") else "Unknown",
                    "session": metadata_div.find("span", class_="session-date").text.strip() if metadata_div.find("span", class_="session-date") else None,
                    "gender": metadata_div.find("span", class_="gender").text.strip() if metadata_div.find("span", class_="gender") else None
                }
            else:
                logger.warning("Metadata section not found")

            # Общее состояние
            general_state_section = soup.find("div", class_="section-general-state")  # Замените на реальный класс
            if general_state_section:
                logger.info("Found general state section")
                systems = general_state_section.find_all("div", class_="system-data")  # Замените на реальный класс
                system_list = []
                for system in systems:
                    system_list.append({
                        "name": system.find("span", class_="system-name").text.strip() if system.find("span", class_="system-name") else None,
                        "status": system.find("span", class_="system-status").text.strip() if system.find("span", class_="system-status") else None,
                        "value": system.find("span", class_="system-value").text.strip() if system.find("span", class_="system-value") else None
                    })
                data["report"]["general_state"]["systems"] = system_list
                data["report"]["general_state"]["condition"] = general_state_section.find("span", class_="condition").text.strip() if general_state_section.find("span", class_="condition") else None
                data["report"]["general_state"]["ph_balance"] = general_state_section.find("span", class_="ph-balance").text.strip() if general_state_section.find("span", class_="ph-balance") else None
                data["report"]["general_state"]["nervous_system"] = general_state_section.find("span", class_="nervous-system").text.strip() if general_state_section.find("span", class_="nervous-system") else None
            else:
                logger.warning("General state section not found")

            # Диаграмма
            diagram_section = soup.find("div", class_="section-diagram")  # Замените на реальный класс
            if diagram_section:
                logger.info("Found diagram section")
                organs = diagram_section.find_all("div", class_="organ-data")  # Замените на реальный класс
                organ_list = []
                for organ in organs:
                    organ_list.append({
                        "id": organ.find("span", class_="organ-id").text.strip() if organ.find("span", class_="organ-id") else None,
                        "name": organ.find("span", class_="organ-name").text.strip() if organ.find("span", class_="organ-name") else None,
                        "status": organ.find("span", class_="organ-status").text.strip() if organ.find("span", class_="organ-status") else None,
                        "value": organ.find("span", class_="organ-value").text.strip() if organ.find("span", class_="organ-value") else None
                    })
                data["report"]["diagram"]["organs"] = organ_list
            else:
                logger.warning("Diagram section not found")

            # Позвоночник
            spine_section = soup.find("div", class_="section-spine")  # Замените на реальный класс
            if spine_section:
                logger.info("Found spine section")
                vertebrae = spine_section.find_all("div", class_="vertebra-data")  # Замените на реальный класс
                vertebra_list = []
                for vertebra in vertebrae:
                    vertebra_list.append({
                        "name": vertebra.find("span", class_="vertebra-name").text.strip() if vertebra.find("span", class_="vertebra-name") else None,
                        "value": vertebra.find("span", class_="vertebra-value").text.strip() if vertebra.find("span", class_="vertebra-value") else None
                    })
                data["report"]["spine"]["vertebrae"] = vertebra_list
                data["report"]["spine"]["issues"] = [issue.text.strip() for issue in spine_section.find_all("li", class_="spine-issue")] if spine_section.find_all("li", class_="spine-issue") else []
            else:
                logger.warning("Spine section not found")

            # Вероятностные отягощения (патогены)
            pathogen_section = soup.find("div", class_="section-pathogens")  # Замените на реальный класс
            if pathogen_section:
                logger.info("Found pathogens section")
                pathogens = pathogen_section.find_all("div", class_="pathogen-data")  # Замените на реальный класс
                for pathogen in pathogens:
                    data["report"]["pathogens"].append({
                        "type": pathogen.find("span", class_="pathogen-type").text.strip() if pathogen.find("span", class_="pathogen-type") else None,
                        "name": pathogen.find("span", class_="pathogen-name").text.strip() if pathogen.find("span", class_="pathogen-name") else None,
                        "probability": pathogen.find("span", class_="pathogen-probability").text.strip() if pathogen.find("span", class_="pathogen-probability") else None,
                        "target_organ": pathogen.find("span", class_="pathogen-target").text.strip() if pathogen.find("span", class_="pathogen-target") else None
                    })
            else:
                logger.warning("Pathogens section not found")

            # Предполагаемые изменения
            changes_section = soup.find("div", class_="section-changes")  # Замените на реальный класс
            if changes_section:
                logger.info("Found changes section")
                data["report"]["changes"] = [change.text.strip() for change in changes_section.find_all("li", class_="change-item")] if changes_section.find_all("li", class_="change-item") else []
            else:
                logger.warning("Changes section not found")

            # Биологический возраст
            bio_age_section = soup.find("div", class_="section-bio-age")  # Замените на реальный класс
            if bio_age_section:
                logger.info("Found bio age section")
                data["report"]["bio_age"] = {
                    "real_age": bio_age_section.find("span", class_="real-age").text.strip() if bio_age_section.find("span", class_="real-age") else None,
                    "bio_age": bio_age_section.find("span", class_="bio-age").text.strip() if bio_age_section.find("span", class_="bio-age") else None,
                    "aging_coefficient": bio_age_section.find("span", class_="aging-coefficient").text.strip() if bio_age_section.find("span", class_="aging-coefficient") else None,
                    "causes": [cause.text.strip() for cause in bio_age_section.find_all("li", class_="aging-cause")] if bio_age_section.find_all("li", class_="aging-cause") else []
                }
            else:
                logger.warning("Bio age section not found")

            # Витамины
            vitamins_section = soup.find("div", class_="section-vitamins")  # Замените на реальный класс
            if vitamins_section:
                logger.info("Found vitamins section")
                vitamins = vitamins_section.find_all("div", class_="vitamin-data")  # Замените на реальный класс
                for vitamin in vitamins:
                    data["report"]["vitamins"].append({
                        "name": vitamin.find("span", class_="vitamin-name").text.strip() if vitamin.find("span", class_="vitamin-name") else None,
                        "level": vitamin.find("span", class_="vitamin-level").text.strip() if vitamin.find("span", class_="vitamin-level") else None,
                        "description": vitamin.find("p", class_="vitamin-description").text.strip() if vitamin.find("p", class_="vitamin-description") else None
                    })
            else:
                logger.warning("Vitamins section not found")

            # Токсические нагрузки
            toxins_section = soup.find("div", class_="section-toxins")  # Замените на реальный класс
            if toxins_section:
                logger.info("Found toxins section")
                data["report"]["toxins"] = [toxin.text.strip() for toxin in toxins_section.find_all("li", class_="toxin-item")] if toxins_section.find_all("li", class_="toxin-item") else []
            else:
                logger.warning("Toxins section not found")

            # Аминокислоты
            amino_section = soup.find("div", class_="section-amino-acids")  # Замените на реальный класс
            if amino_section:
                logger.info("Found amino acids section")
                amino_acids = amino_section.find_all("div", class_="amino-data")  # Замените на реальный класс
                for amino in amino_acids:
                    data["report"]["amino_acids"].append({
                        "name": amino.find("span", class_="amino-name").text.strip() if amino.find("span", class_="amino-name") else None,
                        "description": amino.find("p", class_="amino-description").text.strip() if amino.find("p", class_="amino-description") else None
                    })
            else:
                logger.warning("Amino acids section not found")

            # Психосоматика
            psycho_section = soup.find("div", class_="section-psychosomatics")  # Замените на реальный класс
            if psycho_section:
                logger.info("Found psychosomatics section")
                programs = psycho_section.find_all("div", class_="program-data")  # Замените на реальный класс
                for program in programs:
                    data["report"]["psychosomatics"].append({
                        "program_id": program.find("span", class_="program-id").text.strip() if program.find("span", class_="program-id") else None,
                        "description": program.find("p", class_="program-description").text.strip() if program.find("p", class_="program-description") else None,
                        "affected_organs": [organ.text.strip() for organ in program.find_all("li", class_="affected-organ")] if program.find_all("li", class_="affected-organ") else [],
                        "chakras": [chakra.text.strip() for chakra in program.find_all("li", class_="chakra")] if program.find_all("li", class_="chakra") else []
                    })
            else:
                logger.warning("Psychosomatics section not found")

            # Измененная реактивность
            reactivity_section = soup.find("div", class_="section-reactivity")  # Замените на реальный класс
            if reactivity_section:
                logger.info("Found reactivity section")
                markers = reactivity_section.find_all("div", class_="marker-data")  # Замените на реальный класс
                for marker in markers:
                    data["report"]["reactivity"].append({
                        "marker_id": marker.find("span", class_="marker-id").text.strip() if marker.find("span", class_="marker-id") else None,
                        "description": marker.find("p", class_="marker-description").text.strip() if marker.find("p", class_="marker-description") else None,
                        "recommendations": [rec.text.strip() for rec in marker.find_all("li", class_="recommendation")] if marker.find_all("li", class_="recommendation") else []
                    })
            else:
                logger.warning("Reactivity section not found")

            # Зодиакальная диета
            zodiac_section = soup.find("div", class_="section-zodiac-diet")  # Замените на реальный класс
            if zodiac_section:
                logger.info("Found zodiac diet section")
                data["report"]["zodiac_diet"] = {
                    "sign": zodiac_section.find("span", class_="zodiac-sign").text.strip() if zodiac_section.find("span", class_="zodiac-sign") else None,
                    "description": zodiac_section.find("p", class_="zodiac-description").text.strip() if zodiac_section.find("p", class_="zodiac-description") else None,
                    "menu": [item.text.strip() for item in zodiac_section.find_all("li", class_="menu-item")] if zodiac_section.find_all("li", class_="menu-item") else []
                }
            else:
                logger.warning("Zodiac diet section not found")

            # Водный баланс
            water_section = soup.find("div", class_="section-water-balance")  # Замените на реальный класс
            if water_section:
                logger.info("Found water balance section")
                data["report"]["water_balance"] = {
                    "recommended_intake": water_section.find("span", class_="water-intake").text.strip() if water_section.find("span", class_="water-intake") else None,
                    "organ_levels": [
                        {
                            "organ": organ.find("span", class_="organ-name").text.strip() if organ.find("span", class_="organ-name") else None,
                            "level": organ.find("span", class_="organ-level").text.strip() if organ.find("span", class_="organ-level") else None
                        } for organ in water_section.find_all("div", class_="organ-water-data")
                    ]
                }
            else:
                logger.warning("Water balance section not found")

            # Энергосистема (чакры)
            energy_section = soup.find("div", class_="section-energy-system")  # Замените на реальный класс
            if energy_section:
                logger.info("Found energy system section")
                chakras = energy_section.find_all("div", class_="chakra-data")  # Замените на реальный класс
                chakra_list = []
                for chakra in chakras:
                    chakra_list.append({
                        "name": chakra.find("span", class_="chakra-name").text.strip() if chakra.find("span", class_="chakra-name") else None,
                        "status": chakra.find("span", class_="chakra-status").text.strip() if chakra.find("span", class_="chakra-status") else None,
                        "level": chakra.find("span", class_="chakra-level").text.strip() if chakra.find("span", class_="chakra-level") else None
                    })
                data["report"]["energy_system"]["chakras"] = chakra_list
                data["report"]["energy_system"]["energy_level"] = energy_section.find("span", class_="energy-level").text.strip() if energy_section.find("span", class_="energy-level") else None
            else:
                logger.warning("Energy system section not found")

            # Аурограмма
            auragram_section = soup.find("div", class_="section-auragram")  # Замените на реальный класс
            if auragram_section:
                logger.info("Found auragram section")
                organs = auragram_section.find_all("div", class_="auragram-organ")  # Замените на реальный класс
                organ_list = []
                for organ in organs:
                    organ_list.append({
                        "id": organ.find("span", class_="organ-id").text.strip() if organ.find("span", class_="organ-id") else None,
                        "name": organ.find("span", class_="organ-name").text.strip() if organ.find("span", class_="organ-name") else None,
                        "value": organ.find("span", class_="organ-value").text.strip() if organ.find("span", class_="organ-value") else None
                    })
                data["report"]["auragram"]["organs"] = organ_list
            else:
                logger.warning("Auragram section not found")

            # Динамика
            dynamics_section = soup.find("div", class_="section-dynamics")  # Замените на реальный класс
            if dynamics_section:
                logger.info("Found dynamics section")
                data["report"]["dynamics"]["status"] = dynamics_section.find("p", class_="dynamics-status").text.strip() if dynamics_section.find("p", class_="dynamics-status") else None
            else:
                logger.warning("Dynamics section not found")

            # Ранжирование
            ranking_section = soup.find("div", class_="section-ranking")  # Замените на реальный класс
            if ranking_section:
                logger.info("Found ranking section")
                organs = ranking_section.find_all("div", class_="ranking-organ")  # Замените на реальный класс
                organ_list = []
                for organ in organs:
                    organ_list.append({
                        "name": organ.find("span", class_="organ-name").text.strip() if organ.find("span", class_="organ-name") else None,
                        "value": organ.find("span", class_="organ-value").text.strip() if organ.find("span", class_="organ-value") else None,
                        "percentage": organ.find("span", class_="organ-percentage").text.strip() if organ.find("span", class_="organ-percentage") else None
                    })
                data["report"]["ranking"]["organs"] = organ_list
            else:
                logger.warning("Ranking section not found")

            # Система разбаланса
            imbalance_section = soup.find("div", class_="section-imbalance")  # Замените на реальный класс
            if imbalance_section:
                logger.info("Found imbalance system section")
                systems = imbalance_section.find_all("div", class_="imbalance-system")  # Замените на реальный класс
                system_list = []
                for system in systems:
                    organs = system.find_all("div", class_="imbalance-organ")  # Замените на реальный класс
                    organ_list = []
                    for organ in organs:
                        organ_list.append({
                            "name": organ.find("span", class_="organ-name").text.strip() if organ.find("span", class_="organ-name") else None,
                            "percentage": organ.find("span", class_="organ-percentage").text.strip() if organ.find("span", class_="organ-percentage") else None
                        })
                    system_list.append({
                        "system_name": system.find("span", class_="system-name").text.strip() if system.find("span", class_="system-name") else None,
                        "organs": organ_list
                    })
                data["report"]["imbalance_system"]["systems"] = system_list
            else:
                logger.warning("Imbalance system section not found")

            # Извлечение таблиц
            tables = soup.find_all("table")
            table_data = []
            for table in tables:
                rows = []
                for row in table.find_all("tr"):
                    cols = [col.text.strip() for col in row.find_all("td")]
                    if cols:
                        rows.append(cols)
                if rows:
                    table_data.append(rows)
            if table_data:
                logger.info(f"Found {len(table_data)} tables")
                data["report"]["tables"] = table_data
            else:
                logger.warning("No tables found")

            return data

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to fetch data: {str(e)}")
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")

# Эндпоинт для извлечения и сохранения данных
@app.get("/fetch-report/")
async def fetch_and_store_report(url: str):
    try:
        # Извлекаем test_id из URL
        test_id = url.split("testId=")[1].split("&")[0]
        logger.info(f"Processing test_id: {test_id}")

        # Проверяем, существует ли отчет
        existing = await collection.find_one({"test_id": test_id})
        if existing:
            logger.info(f"Report with test_id {test_id} already exists")
            return {
                "message": "Report already exists",
                "document_id": str(existing["_id"]),
                "report": existing["report"]
            }

        # Извлекаем данные
        report_data = await fetch_report(url)

        # Сохраняем в MongoDB
        result = await collection.insert_one(report_data)
        logger.info(f"Inserted document with ID: {result.inserted_id}")

        # Возвращаем полный отчет
        return {
            "message": "Report saved successfully",
            "document_id": str(result.inserted_id),
            "report": report_data["report"]
        }

    except Exception as e:
        logger.error(f"Error in fetch_and_store_report: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# Закрытие подключения к MongoDB
@app.on_event("shutdown")
async def shutdown_event():
    client.close()
    logger.info("MongoDB connection closed")
