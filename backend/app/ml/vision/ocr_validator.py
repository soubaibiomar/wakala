import logging

logger = logging.getLogger(__name__)

class OCRValidator:
    """
    Simule ou utilise Tesseract pour scanner le Certificat de Cession
    et vérifier la correspondance avec l'identité du Vendeur.
    """

    @staticmethod
    def extract_text(image_path_or_bytes) -> str:
        """
        Dans un cas réel : 
        import pytesseract
        from PIL import Image
        return pytesseract.image_to_string(Image.open(image_path_or_bytes))
        
        Ici, nous simulons l'extraction OCR par sécurité (fallback).
        """
        # Mock d'extraction
        logger.info("Exécution du scan OCR...")
        return "CERTIFICAT DE CESSION\nNom du vendeur : OMAR BENALI\nAcheteur : YOUSSEF ALAOUI\nVéhicule : VOLKSWAGEN GOLF\nDate : 2026-07-14"

    @staticmethod
    def validate_ownership_transfer(document_text: str, seller_name: str) -> bool:
        """
        Vérifie si le nom du vendeur enregistré sur la plateforme
        apparaît bien dans le texte scanné du certificat de cession.
        """
        if not seller_name:
            return False
            
        # Normalisation pour la comparaison
        normalized_doc = document_text.lower()
        
        # Le nom du vendeur est souvent stocké sous forme "Omar Benali"
        # On peut vérifier la présence du nom ou prénom complet ou séparé.
        seller_parts = seller_name.lower().split()
        
        # Logique de matching basique : on veut au moins que le nom de famille ou prénom apparaisse
        # Dans la réalité, on utiliserait du Fuzzy Matching (Levenshtein) pour palier aux erreurs d'OCR.
        matches = [part for part in seller_parts if part in normalized_doc]
        
        if len(matches) > 0:
            logger.info(f"Transfert de propriété validé via OCR pour : {seller_name}")
            return True
        else:
            logger.warning(f"Échec de validation OCR : Le nom '{seller_name}' n'a pas été trouvé dans le document.")
            return False

ocr_validator = OCRValidator()
