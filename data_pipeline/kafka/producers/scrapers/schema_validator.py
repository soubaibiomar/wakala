import logging
from typing import Dict, Any, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class SchemaValidator:
    """Validates scraped listing data before publication"""
    
    @staticmethod
    def validate(listing: Dict[str, Any]) -> Tuple[bool, list[str]]:
        """
        Validates listing fields.
        Returns: (is_valid, list_of_errors)
        """
        errors = []
        
        # 1. Required fields
        required = ["brand", "source_url", "source"]
        for field in required:
            val = listing.get(field)
            if not val or val == "unknown" or val == "N/A":
                errors.append(f"Missing required field: {field}")
                
        # 2. Price validation
        price = listing.get("price")
        if price is not None:
            if not isinstance(price, (int, float)):
                errors.append(f"Price must be a number, got {type(price)}")
            elif price < 5000 or price > 20000000:
                errors.append(f"Price {price} out of realistic range [5000, 20000000]")
        else:
            errors.append("Missing price")
            
        # 3. Year validation
        year = listing.get("year")
        if year is not None:
            if not isinstance(year, int):
                errors.append(f"Year must be an int, got {type(year)}")
            else:
                current_year = datetime.now().year
                if year < 1990 or year > current_year + 1:
                    errors.append(f"Year {year} out of bounds [1990, {current_year+1}]")
                    
        # 4. Mileage validation
        mileage = listing.get("mileage")
        if mileage is not None:
            if not isinstance(mileage, (int, float)):
                errors.append(f"Mileage must be numeric")
            elif mileage < 0 or mileage > 1000000:
                errors.append(f"Mileage {mileage} out of bounds")
        # 5. Trust fields validation
        warranty_months = listing.get("warranty_months")
        if warranty_months is not None:
            if not isinstance(warranty_months, int):
                errors.append(f"warranty_months must be an int, got {type(warranty_months)}")
            elif warranty_months < 0 or warranty_months > 120:
                errors.append(f"warranty_months {warranty_months} out of realistic range")
                
        inspection_points = listing.get("inspection_points")
        if inspection_points is not None:
            if not isinstance(inspection_points, int):
                errors.append(f"inspection_points must be an int, got {type(inspection_points)}")
            elif inspection_points <= 0 or inspection_points > 500:
                errors.append(f"inspection_points {inspection_points} out of realistic range")

        is_valid = len(errors) == 0
        return is_valid, errors
