import json
import uuid

elements = []

def add_rect(x, y, w, h, text, bg="#ffffff", fg="#000000", id=None):
    if not id: id = str(uuid.uuid4())
    rect = {
        "id": id,
        "type": "rectangle",
        "x": x, "y": y,
        "width": w, "height": h,
        "strokeColor": fg,
        "backgroundColor": bg,
        "fillStyle": "solid",
        "strokeWidth": 1,
        "strokeStyle": "solid",
        "roughness": 0,
        "opacity": 100,
        "groupIds": [],
        "strokeSharpness": "round",
        "seed": 1,
        "version": 1,
        "versionNonce": 1,
        "isDeleted": False,
        "boundElements": []
    }
    
    text_id = str(uuid.uuid4())
    text_el = {
        "id": text_id,
        "type": "text",
        "x": x + 10, "y": y + (h/2) - 10,
        "width": w - 20, "height": 20,
        "strokeColor": fg,
        "backgroundColor": "transparent",
        "fillStyle": "hachure",
        "strokeWidth": 1,
        "strokeStyle": "solid",
        "roughness": 0,
        "opacity": 100,
        "groupIds": [],
        "strokeSharpness": "sharp",
        "seed": 1,
        "version": 1,
        "versionNonce": 1,
        "isDeleted": False,
        "boundElements": None,
        "text": text,
        "fontSize": 16,
        "fontFamily": 1,
        "textAlign": "center",
        "verticalAlign": "middle",
        "baseline": 15,
        "containerId": id
    }
    rect["boundElements"].append({"type": "text", "id": text_id})
    elements.extend([rect, text_el])
    return id

def add_arrow(start_id, end_id, x1, y1, x2, y2):
    arr_id = str(uuid.uuid4())
    arrow = {
        "id": arr_id,
        "type": "arrow",
        "x": x1, "y": y1,
        "width": abs(x2-x1), "height": abs(y2-y1),
        "strokeColor": "#000000",
        "backgroundColor": "transparent",
        "fillStyle": "hachure",
        "strokeWidth": 1,
        "strokeStyle": "solid",
        "roughness": 0,
        "opacity": 100,
        "groupIds": [],
        "strokeSharpness": "round",
        "seed": 1,
        "version": 1,
        "versionNonce": 1,
        "isDeleted": False,
        "boundElements": None,
        "points": [[0, 0], [x2-x1, y2-y1]],
        "startBinding": {"elementId": start_id, "focus": -0.5, "gap": 5},
        "endBinding": {"elementId": end_id, "focus": -0.5, "gap": 5},
        "startArrowhead": None,
        "endArrowhead": "arrow"
    }
    elements.append(arrow)

# Scraper Architecture
r_avito = add_rect(100, 100, 200, 50, "Sites Web (Avito, Moteur.ma)", bg="#e1f5fe")
r_parser = add_rect(100, 200, 200, 50, "JSON-LD Parser", bg="#fff9c4")
r_llm = add_rect(100, 300, 200, 50, "Fallback: GPT-4o-mini", bg="#ffcdd2")
r_model = add_rect(100, 400, 200, 50, "Pydantic Model (Structuré)", bg="#c8e6c9")

add_arrow(r_avito, r_parser, 200, 150, 200, 200)
add_arrow(r_parser, r_llm, 200, 250, 200, 300)
add_arrow(r_llm, r_model, 200, 350, 200, 400)
add_arrow(r_parser, r_model, 300, 225, 300, 425)

# Pipeline Architecture
r_producer = add_rect(400, 100, 200, 50, "Scraper Producer", bg="#e1f5fe")
r_kafka = add_rect(400, 200, 200, 50, "Kafka (listings.raw)", bg="#ffe0b2")
r_consumer = add_rect(400, 300, 200, 50, "Listing Consumer", bg="#e1f5fe")
r_bronze = add_rect(400, 400, 200, 50, "Bronze Storage (.parquet)", bg="#bcaaa4")
r_spark = add_rect(700, 400, 200, 50, "Spark Streaming (Clean Job)", bg="#ffcc80")
r_silver = add_rect(700, 500, 200, 50, "Silver Storage (Nettoyé)", bg="#cfd8dc")
r_airflow = add_rect(700, 600, 200, 50, "Airflow (Aggregation)", bg="#90caf9")
r_gold = add_rect(700, 700, 200, 50, "Gold Storage (Prêt ML)", bg="#ffeb3b")

add_arrow(r_model, r_producer, 300, 425, 400, 125)
add_arrow(r_producer, r_kafka, 500, 150, 500, 200)
add_arrow(r_kafka, r_consumer, 500, 250, 500, 300)
add_arrow(r_consumer, r_bronze, 500, 350, 500, 400)
add_arrow(r_bronze, r_spark, 600, 425, 700, 425)
add_arrow(r_spark, r_silver, 800, 450, 800, 500)
add_arrow(r_silver, r_airflow, 800, 550, 800, 600)
add_arrow(r_airflow, r_gold, 800, 650, 800, 700)

excalidraw = {
    "type": "excalidraw",
    "version": 2,
    "source": "https://excalidraw.com",
    "elements": elements,
    "appState": {"viewBackgroundColor": "#f8f9fa"},
    "files": {}
}

with open("d:/Projet automobile/vente-auto-platform/Livrables/Wakala_Architecture.excalidraw", "w", encoding="utf-8") as f:
    json.dump(excalidraw, f, indent=2)

print("Excalidraw file generated successfully!")
