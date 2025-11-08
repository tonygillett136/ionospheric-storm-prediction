"""
Regional Prediction Approach Experiment

Scientific comparison of two regional prediction approaches:
- Approach A: Climatology-primary with regional factors
- Approach B: V2.1 ML-enhanced with regional adjustments

This script runs a comprehensive backtest on 90 days of historical data
across all 5 geographic regions and documents the results.
"""
import asyncio
import logging
from datetime import datetime, timedelta
import json
from pathlib import Path

from app.db.database import AsyncSessionLocal, init_db
from app.services.geographic_climatology_service import GeographicClimatologyService
from app.services.regional_backtest_service import RegionalBacktestService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def run_experiment():
    """Run the regional prediction experiment"""
    logger.info("="*80)
    logger.info("REGIONAL PREDICTION APPROACH EXPERIMENT")
    logger.info("="*80)
    
    # Initialize database
    await init_db()
    
    # Initialize services
    async with AsyncSessionLocal() as session:
        logger.info("\n1. Initializing Geographic Climatology Service...")
        geo_climatology = GeographicClimatologyService()
        await geo_climatology.build_climatology(session)
        logger.info("✓ Climatology service initialized")
        
        logger.info("\n2. Initializing Regional Backtest Service...")
        backtest_service = RegionalBacktestService(
            geographic_climatology=geo_climatology,
            model_path="models/v2/best_model.keras"
        )
        logger.info("✓ Backtest service initialized")
        
        # Define test period: Last 90 days
        end_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = end_date - timedelta(days=90)
        
        logger.info(f"\n3. Running Experiment")
        logger.info(f"   Test Period: {start_date.date()} to {end_date.date()}")
        logger.info(f"   Duration: 90 days")
        logger.info(f"   Regions: 5 (Equatorial, Mid-Latitude, Auroral, Polar, Global)")
        logger.info(f"   Sample Interval: Every 6 hours")
        logger.info(f"\n   This will take several minutes...")
        
        # Run the backtest
        results = await backtest_service.run_regional_backtest(
            session,
            start_date,
            end_date,
            sample_interval_hours=6
        )
        
        # Save results to file
        results_file = Path("REGIONAL_EXPERIMENT_RESULTS.json")
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"\n✓ Experiment complete! Results saved to {results_file}")
        
        # Print summary
        print_results_summary(results)
        
        # Generate markdown documentation
        generate_markdown_report(results)
        
        return results


def print_results_summary(results: dict):
    """Print a summary of the experiment results"""
    print("\n" + "="*80)
    print("EXPERIMENT RESULTS SUMMARY")
    print("="*80)
    
    print(f"\nTest Period: {results['period']['start']} to {results['period']['end']}")
    print(f"Total Hours: {results['period']['total_hours']:.1f}")
    
    print("\n" + "-"*80)
    print("REGIONAL COMPARISON")
    print("-"*80)
    
    for region_code, comparison in results.get('comparison', {}).items():
        print(f"\n{comparison['region']}:")
        print(f"  Winner: {comparison['winner']}")
        print(f"  MAE Improvement: {comparison['mae_improvement']:+.3f} TECU")
        print(f"  RMSE Improvement: {comparison['rmse_improvement']:+.3f} TECU")
        print(f"  Confidence: {comparison['confidence']}")
        
        # Show detailed metrics
        clim = results['approaches']['climatology_primary'].get(region_code, {})
        v21 = results['approaches']['v21_enhanced'].get(region_code, {})
        
        print(f"\n  Climatology-Primary:")
        print(f"    MAE:  {clim.get('mae', 0):.3f} TECU")
        print(f"    RMSE: {clim.get('rmse', 0):.3f} TECU")
        
        print(f"  V2.1-Enhanced:")
        print(f"    MAE:  {v21.get('mae', 0):.3f} TECU")
        print(f"    RMSE: {v21.get('rmse', 0):.3f} TECU")
    
    print("\n" + "="*80)
    print("OVERALL WINNER")
    print("="*80)
    
    overall = results.get('overall_winner', {})
    print(f"\nWinner: {overall.get('approach', 'Unknown')}")
    print(f"Total Improvement: {overall.get('total_improvement', 0):+.3f} TECU")
    print(f"\nRecommendation:")
    print(f"  {overall.get('recommendation', 'No recommendation available')}")
    print("\n" + "="*80)


def generate_markdown_report(results: dict):
    """Generate a markdown report of the experiment"""
    report_file = Path("REGIONAL_EXPERIMENT_REPORT.md")
    
    with open(report_file, 'w') as f:
        f.write("# Regional Prediction Approach Experiment\n\n")
        f.write("## Executive Summary\n\n")
        
        overall = results.get('overall_winner', {})
        f.write(f"**Winner:** {overall.get('approach', 'Unknown')}\n\n")
        f.write(f"**Recommendation:** {overall.get('recommendation', 'No recommendation')}\n\n")
        
        f.write("## Experimental Design\n\n")
        f.write("### Approaches Tested\n\n")
        f.write("**Approach A: Climatology-Primary**\n")
        f.write("- Uses regional climatology as baseline\n")
        f.write("- Applies physics-based regional adjustment factors\n")
        f.write("- Best for: Stable conditions, regional baselines\n\n")
        
        f.write("**Approach B: V2.1 ML-Enhanced**\n")
        f.write("- Runs V2.1 neural network for global prediction\n")
        f.write("- Applies regional adjustments to ML output\n")
        f.write("- Blends with regional climatology (weight varies with Kp)\n")
        f.write("- Best for: Storm dynamics, rapid changes\n\n")
        
        f.write("### Test Parameters\n\n")
        f.write(f"- **Test Period:** {results['period']['start']} to {results['period']['end']}\n")
        f.write(f"- **Duration:** 90 days\n")
        f.write(f"- **Total Hours:** {results['period']['total_hours']:.1f}\n")
        f.write(f"- **Sample Interval:** Every 6 hours\n")
        f.write(f"- **Regions Tested:** 5 (Equatorial, Mid-Latitude, Auroral, Polar, Global)\n")
        f.write(f"- **Metrics:** MAE, RMSE, Median Error, Max Error\n\n")
        
        f.write("## Results by Region\n\n")
        
        for region_code, comparison in results.get('comparison', {}).items():
            f.write(f"### {comparison['region']}\n\n")
            f.write(f"**Winner:** {comparison['winner']} ({comparison['confidence']} confidence)\n\n")
            
            clim = results['approaches']['climatology_primary'].get(region_code, {})
            v21 = results['approaches']['v21_enhanced'].get(region_code, {})
            
            f.write("| Metric | Climatology-Primary | V2.1-Enhanced | Improvement |\n")
            f.write("|--------|---------------------|---------------|-------------|\n")
            f.write(f"| MAE (TECU) | {clim.get('mae', 0):.3f} | {v21.get('mae', 0):.3f} | {comparison['mae_improvement']:+.3f} |\n")
            f.write(f"| RMSE (TECU) | {clim.get('rmse', 0):.3f} | {v21.get('rmse', 0):.3f} | {comparison['rmse_improvement']:+.3f} |\n")
            f.write(f"| Median Error | {clim.get('median_error', 0):.3f} | {v21.get('median_error', 0):.3f} | - |\n")
            f.write(f"| Max Error | {clim.get('max_error', 0):.3f} | {v21.get('max_error', 0):.3f} | - |\n")
            f.write(f"| Sample Count | {clim.get('sample_count', 0)} | {v21.get('sample_count', 0)} | - |\n\n")
        
        f.write("## Overall Conclusion\n\n")
        f.write(f"**Winner:** {overall.get('approach', 'Unknown')}\n\n")
        f.write(f"**Total Improvement:** {overall.get('total_improvement', 0):+.3f} TECU\n\n")
        f.write(f"**Production Recommendation:**\n\n")
        f.write(f"{overall.get('recommendation', 'No recommendation')}\n\n")
        
        f.write("## Interpretation\n\n")
        f.write("- Positive improvement values indicate V2.1-Enhanced performs better\n")
        f.write("- Negative improvement values indicate Climatology-Primary performs better\n")
        f.write("- MAE (Mean Absolute Error): Average prediction error magnitude\n")
        f.write("- RMSE (Root Mean Square Error): Emphasizes larger errors more heavily\n\n")
        
        f.write("## Files\n\n")
        f.write("- **Results Data:** `REGIONAL_EXPERIMENT_RESULTS.json`\n")
        f.write("- **This Report:** `REGIONAL_EXPERIMENT_REPORT.md`\n")
        f.write("- **Backtest Service:** `backend/app/services/regional_backtest_service.py`\n\n")
        
        f.write("---\n\n")
        f.write(f"*Experiment conducted: {datetime.utcnow().isoformat()}*\n")
    
    logger.info(f"✓ Markdown report generated: {report_file}")


if __name__ == "__main__":
    asyncio.run(run_experiment())
