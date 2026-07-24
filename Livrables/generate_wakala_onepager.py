from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor

def draw_paragraph(c, x, y, text, font, size, color, width, line_height):
    c.setFont(font, size)
    c.setFillColor(color)
    words = text.split(' ')
    lines = []
    current_line = []
    for word in words:
        current_line.append(word)
        if c.stringWidth(' '.join(current_line), font, size) > width:
            current_line.pop()
            lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))
    
    for line in lines:
        c.drawString(x, y, line)
        y -= line_height
    return y

def create_one_pager(filename):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    
    # Colors
    accent_color = HexColor('#1F4FE0')
    text_color = HexColor('#1A1A1A')
    light_text = HexColor('#4A4A4A')
    
    # Fonts
    title_font = "Helvetica-Bold"
    subtitle_font = "Times-Bold"
    body_font = "Helvetica"
    body_bold = "Helvetica-Bold"
    
    # Margins & Layout
    margin_x = 20 * mm
    margin_y = 20 * mm
    col_gap = 10 * mm
    col_width = (width - 2*margin_x - col_gap) / 2
    left_x = margin_x
    right_x = margin_x + col_width + col_gap
    
    # --- HEADER ---
    y_pos = height - margin_y - 20*mm
    c.setFont(title_font, 65)
    c.setFillColor(text_color)
    c.drawString(left_x, y_pos, "Wakala")
    
    c.setFont(body_font, 12)
    c.setFillColor(light_text)
    c.drawString(left_x, y_pos - 8*mm, "Plateforme intelligente de vente automobile")
    
    # Vertical Separator
    y_top = y_pos - 15*mm
    y_bottom = margin_y + 10*mm
    c.setStrokeColor(accent_color)
    c.setLineWidth(0.5)
    c.line(width/2, y_top, width/2, y_bottom)
    
    # --- LEFT COLUMN ---
    curr_y = y_top - 5*mm
    
    # 1. Contexte & Constat
    c.setFont(subtitle_font, 14)
    c.setFillColor(text_color)
    c.drawString(left_x, curr_y, "1. Contexte & Constat")
    curr_y -= 7*mm
    
    p1 = "Le marché marocain oppose deux modèles limités : Avito.ma (volume brut, aucune intelligence) et Moteur.ma (données structurées mais consultatives). Aucun des deux n'offre de recommandation intelligente, de détection de fraude, ni de pricing prédictif."
    curr_y = draw_paragraph(c, left_x, curr_y, p1, body_font, 10, light_text, col_width - 5*mm, 5*mm)
    curr_y -= 8*mm
    
    # 2. Ce qui manque
    c.setFont(subtitle_font, 14)
    c.setFillColor(text_color)
    c.drawString(left_x, curr_y, "2. Ce qui manque au marché local")
    curr_y -= 7*mm
    
    bullets = [
        "Recommandation intelligente",
        "Détection de fraude / score de confiance",
        "Pricing prédictif en temps réel"
    ]
    for b in bullets:
        c.setFillColor(accent_color)
        c.setFont(body_font, 14)
        c.drawString(left_x, curr_y - 1*mm, "•")
        c.setFillColor(light_text)
        c.setFont(body_font, 10)
        c.drawString(left_x + 5*mm, curr_y, b)
        curr_y -= 6*mm
    curr_y -= 6*mm
    
    # 3. Tendance internationale
    c.setFont(subtitle_font, 14)
    c.setFillColor(text_color)
    c.drawString(left_x, curr_y, "3. Tendance internationale")
    curr_y -= 7*mm
    
    p3 = "Carvana (IA-driven), CarGurus et CarMax (hybrides) convergent vers un modèle commun : une fondation Big Data couplée à une couche d'IA générative et conversationnelle."
    curr_y = draw_paragraph(c, left_x, curr_y, p3, body_font, 10, light_text, col_width - 5*mm, 5*mm)
    curr_y -= 8*mm
    
    # 4. Opportunité
    c.setFont(subtitle_font, 14)
    c.setFillColor(text_color)
    c.drawString(left_x, curr_y, "4. Opportunité pour Wakala")
    curr_y -= 7*mm
    
    p4 = "Architecture hybride native dès la conception : un avantage concurrentiel majeur de premier entrant sur le marché marocain."
    curr_y = draw_paragraph(c, left_x, curr_y, p4, body_font, 10, light_text, col_width - 5*mm, 5*mm)
    
    # --- RIGHT COLUMN ---
    curr_y = y_top - 5*mm
    
    # 1. Tableau comparatif
    c.setFont(subtitle_font, 14)
    c.setFillColor(text_color)
    c.drawString(right_x, curr_y, "Benchmark Concurrentiel")
    curr_y -= 10*mm
    
    headers = ["Plateforme", "Marché", "Classification", "Argument clé"]
    x_offsets = [0, 18*mm, 28*mm, 50*mm]
    
    c.setFont(body_bold, 8)
    c.setFillColor(text_color)
    for i, h in enumerate(headers):
        c.drawString(right_x + x_offsets[i], curr_y, h)
    curr_y -= 6*mm
    
    rows = [
        ("Avito.ma", "MA", "Généraliste", "Volume brut"),
        ("Moteur.ma", "MA", "Spécialisé", "Données structur."),
        ("Carvana", "US", "Digital", "IA-driven, online"),
        ("CarGurus", "US", "Hybride", "Transparence prix"),
        ("CarMax", "US", "Hybride", "Omnicanal omni-IA"),
        ("Wakala", "MA", "Intelligente", "Big Data + IA Native")
    ]
    
    for row in rows:
        is_wakala = (row[0] == "Wakala")
        c.setFont(body_bold if is_wakala else body_font, 8)
        
        for i, val in enumerate(row):
            if is_wakala and i == 0:
                c.setFillColor(accent_color)
            else:
                c.setFillColor(text_color if is_wakala else light_text)
            c.drawString(right_x + x_offsets[i], curr_y, val)
        curr_y -= 7*mm
        
    curr_y -= 10*mm
    
    # 2. Architecture Wakala
    c.setFont(subtitle_font, 14)
    c.setFillColor(text_color)
    c.drawString(right_x, curr_y, "Architecture Wakala (5 Couches)")
    curr_y -= 10*mm
    
    arch_layers = [
        ("1. Ingestion temps réel", "Kafka"),
        ("2. Transformation Big Data", "Spark, Airflow"),
        ("3. Stockage / Data Lake", "PostgreSQL, Medallion"),
        ("4. IA & Graphe", "XGBoost, Isolation Forest, Neo4j"),
        ("5. RAG & Interaction", "Qdrant, LangChain, FastAPI")
    ]
    
    for title, tech in arch_layers:
        c.setFont(body_bold, 10)
        c.setFillColor(text_color)
        c.drawString(right_x, curr_y, title)
        curr_y -= 5*mm
        
        c.setFont(body_font, 9)
        c.setFillColor(accent_color)
        c.drawString(right_x + 3*mm, curr_y, tech)
        curr_y -= 8*mm
        
    # --- FOOTER ---
    c.setStrokeColor(HexColor('#E0E0E0'))
    c.setLineWidth(0.5)
    c.line(margin_x, margin_y + 5*mm, width - margin_x, margin_y + 5*mm)
    
    c.setFont(subtitle_font, 8)
    c.setFillColor(light_text)
    c.drawString(margin_x, margin_y, "WAKALA — CONFIDENTIAL & PROPRIETARY")
    
    c.save()

if __name__ == "__main__":
    create_one_pager("d:\\Projet automobile\\Livrables\\Wakala_OnePager.pdf")
    print("PDF generated successfully.")
