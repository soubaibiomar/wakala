import os
import json
import logging
from sqlalchemy import create_engine, text
from tabulate import tabulate

logger = logging.getLogger(__name__)

class HealthSummary:
    """
    Aggregates health metrics from the scraper_health table to provide
    a consolidated dashboard view of all sources (marketplaces + dealers).
    """
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")

    def get_summary(self, limit: int = 50) -> str:
        if not self.db_url:
            return "DATABASE_URL not set. Cannot fetch health summary."
            
        try:
            engine = create_engine(self.db_url)
            with engine.connect() as conn:
                # Check if table exists
                check = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'scraper_health')")).scalar()
                if not check:
                    return "Table 'scraper_health' does not exist yet."

                # Get the latest run for each site
                sql = text("""
                    WITH RankedHealth AS (
                        SELECT 
                            site,
                            run_timestamp,
                            success_rate,
                            total_attempted,
                            total_valid,
                            field_success_rates,
                            ROW_NUMBER() OVER(PARTITION BY site ORDER BY run_timestamp DESC) as rn
                        FROM scraper_health
                    )
                    SELECT * FROM RankedHealth WHERE rn = 1
                    ORDER BY success_rate ASC, site ASC
                    LIMIT :limit
                """)
                
                result = conn.execute(sql, {"limit": limit})
                rows = result.fetchall()
                
                if not rows:
                    return "No health data available yet."

                total_sources = len(rows)
                active_sources = sum(1 for r in rows if r.total_attempted > 0)
                degraded_sources = sum(1 for r in rows if float(r.success_rate) < 0.5 and r.total_attempted > 0)
                avg_success = sum(float(r.success_rate) for r in rows if r.total_attempted > 0) / (active_sources or 1)

                header = (
                    f"=== SCRAPER HEALTH SUMMARY ===\n"
                    f"Total Sources: {total_sources} | Active (data fetched): {active_sources}\n"
                    f"Degraded (<50%): {degraded_sources} | Average Success: {avg_success:.1%}\n\n"
                )

                table_data = []
                for row in rows:
                    if row.total_attempted == 0:
                        status = "INACTIVE"
                    elif float(row.success_rate) < 0.5:
                        status = "DEGRADED"
                    else:
                        status = "HEALTHY"
                        
                    table_data.append([
                        row.site,
                        status,
                        f"{float(row.success_rate):.1%}",
                        f"{row.total_valid}/{row.total_attempted}",
                        row.run_timestamp.strftime("%Y-%m-%d %H:%M") if row.run_timestamp else "N/A"
                    ])

                table = tabulate(
                    table_data, 
                    headers=["Source", "Status", "Success Rate", "Valid/Total", "Last Run"],
                    tablefmt="simple"
                )
                
                return header + table
                
        except Exception as e:
            logger.error(f"Error generating health summary: {e}")
            return f"Error generating summary: {e}"

if __name__ == "__main__":
    summary = HealthSummary().get_summary()
    print(summary)
