import sys
import os
import pandas as pd

# Add src to path
sys.path.append(os.path.abspath('src'))

from quality_data_generator import QualityDataGenerator

def test_a3_generation():
    print("Testing A3 Data Generation...")
    
    # Mock equipment data
    equipment_df = pd.DataFrame({'equipment_id': [1], 'equipment_name': ['Test Eq']})
    
    generator = QualityDataGenerator(equipment_df)
    
    # Test Weld Defect
    print("\n[TEST] Generating for 'Weld Defect'...")
    weld_report = generator.generate_a3_report('Weld Defect')
    
    if "Weld defects have increased" in weld_report['background']:
        print("✅ Weld Defect background content verified.")
    else:
        print("❌ Weld Defect background content mismatch.")
        print(weld_report['background'])

    # Test Generic Defect
    print("\n[TEST] Generating for 'Paint Issue' (Generic)...")
    generic_report = generator.generate_a3_report('Paint Issue')
    
    if "Increase in Paint Issue" in generic_report['background']:
        print("✅ Generic Defect background content verified.")
    else:
        print("❌ Generic Defect background content mismatch.")
        print(generic_report['background'])

if __name__ == "__main__":
    test_a3_generation()
