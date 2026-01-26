"""
Quality Control & Six Sigma Data Generator
Generates synthetic quality metrics, SPC data, and defect tracking data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

class QualityDataGenerator:
    """Generate synthetic quality control data for Six Sigma analytics"""
    
    def __init__(self, equipment_df, start_date='2022-01-01', end_date='2024-12-31'):
        self.equipment_df = equipment_df
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)
        self.date_range = pd.date_range(start=self.start_date, end=self.end_date, freq='D')
        
        # Defect types for heavy equipment manufacturing
        self.defect_types = [
            'Weld Defect', 'Paint Finish', 'Hydraulic Leak', 'Electrical Fault',
            'Dimensional Variance', 'Surface Scratch', 'Bolt Torque', 'Alignment Issue',
            'Material Defect', 'Assembly Error', 'Seal Failure', 'Calibration Error'
        ]
        
        self.severity_levels = ['Critical', 'Major', 'Minor']
        
    def generate_spc_data(self, num_samples=5000):
        """Generate Statistical Process Control data (X-bar and R values)"""
        
        records = []
        
        # Quality metrics to monitor
        metrics = [
            {'name': 'Hydraulic Pressure (PSI)', 'target': 3000, 'tolerance': 150},
            {'name': 'Weld Strength (MPa)', 'target': 450, 'tolerance': 30},
            {'name': 'Paint Thickness (microns)', 'target': 120, 'tolerance': 10},
            {'name': 'Bolt Torque (Nm)', 'target': 200, 'tolerance': 15},
            {'name': 'Alignment Deviation (mm)', 'target': 0, 'tolerance': 0.5}
        ]
        
        for _ in range(num_samples):
            date = random.choice(self.date_range)
            equipment = self.equipment_df.sample(1).iloc[0]
            metric = random.choice(metrics)
            
            # Generate subgroup of 5 measurements (standard for X-bar R charts)
            subgroup_size = 5
            
            # Most measurements in control, some out of control
            in_control = random.random() < 0.92  # 92% in control
            
            if in_control:
                # Normal variation around target
                measurements = np.random.normal(
                    metric['target'], 
                    metric['tolerance'] / 3,  # 3-sigma
                    subgroup_size
                )
            else:
                # Out of control - shift in mean or increased variance
                if random.random() < 0.5:
                    # Mean shift
                    shift = random.choice([1, -1]) * metric['tolerance'] * random.uniform(0.8, 1.5)
                    measurements = np.random.normal(
                        metric['target'] + shift,
                        metric['tolerance'] / 3,
                        subgroup_size
                    )
                else:
                    # Increased variance
                    measurements = np.random.normal(
                        metric['target'],
                        metric['tolerance'] * random.uniform(0.5, 0.8),
                        subgroup_size
                    )
            
            xbar = np.mean(measurements)
            r_value = np.max(measurements) - np.min(measurements)
            
            records.append({
                'inspection_id': f"SPC{len(records)+1:06d}",
                'inspection_date': date,
                'equipment_id': equipment['equipment_id'],
                'equipment_name': equipment['equipment_name'],
                'equipment_type': equipment['equipment_type'],
                'metric_name': metric['name'],
                'target_value': metric['target'],
                'tolerance': metric['tolerance'],
                'xbar_value': round(xbar, 2),
                'r_value': round(r_value, 2),
                'measurement_1': round(measurements[0], 2),
                'measurement_2': round(measurements[1], 2),
                'measurement_3': round(measurements[2], 2),
                'measurement_4': round(measurements[3], 2),
                'measurement_5': round(measurements[4], 2),
                'in_control': in_control
            })
        
        return pd.DataFrame(records)
    
    def generate_defect_data(self, num_defects=2000):
        """Generate defect tracking data for Pareto analysis"""
        
        records = []
        
        # Pareto distribution: 20% of defect types cause 80% of problems
        weights = [0.25, 0.20, 0.15, 0.12, 0.08, 0.06, 0.04, 0.03, 0.02, 0.02, 0.02, 0.01]
        
        for i in range(num_defects):
            date = random.choice(self.date_range)
            equipment = self.equipment_df.sample(1).iloc[0]
            defect_type = random.choices(self.defect_types, weights=weights)[0]
            
            # Critical defects are rare
            if defect_type in ['Hydraulic Leak', 'Electrical Fault', 'Seal Failure']:
                severity = random.choices(
                    self.severity_levels, 
                    weights=[0.15, 0.35, 0.50]
                )[0]
            else:
                severity = random.choices(
                    self.severity_levels,
                    weights=[0.05, 0.25, 0.70]
                )[0]
            
            # Cost impact based on severity
            if severity == 'Critical':
                rework_cost = random.uniform(5000, 25000)
                rework_hours = random.uniform(8, 40)
            elif severity == 'Major':
                rework_cost = random.uniform(1000, 8000)
                rework_hours = random.uniform(2, 12)
            else:
                rework_cost = random.uniform(200, 2000)
                rework_hours = random.uniform(0.5, 4)
            
            # Root cause (for fishbone diagrams)
            root_causes = {
                'Man': ['Operator Error', 'Insufficient Training', 'Fatigue'],
                'Machine': ['Tool Wear', 'Calibration Drift', 'Equipment Malfunction'],
                'Material': ['Substandard Material', 'Material Contamination', 'Wrong Specification'],
                'Method': ['Incorrect Procedure', 'Process Not Followed', 'Inadequate Work Instruction'],
                'Measurement': ['Gauge Error', 'Wrong Instrument', 'Calibration Issue'],
                'Environment': ['Temperature Variation', 'Humidity', 'Vibration']
            }
            
            category = random.choice(list(root_causes.keys()))
            root_cause = random.choice(root_causes[category])
            
            records.append({
                'defect_id': f"DEF{i+1:06d}",
                'defect_date': date,
                'equipment_id': equipment['equipment_id'],
                'equipment_type': equipment['equipment_type'],
                'defect_type': defect_type,
                'severity': severity,
                'root_cause_category': category,
                'root_cause': root_cause,
                'rework_cost': round(rework_cost, 2),
                'rework_hours': round(rework_hours, 2),
                'detected_at': random.choice(['In-Process', 'Final Inspection', 'Customer']),
                'status': random.choice(['Open', 'Open', 'In Progress', 'Closed', 'Closed', 'Closed'])
            })
        
        return pd.DataFrame(records)
    
    def generate_process_capability_data(self):
        """Generate process capability data for Cp/Cpk calculations"""
        
        records = []
        
        processes = [
            {'name': 'Hydraulic Cylinder Assembly', 'usl': 3150, 'lsl': 2850, 'target': 3000},
            {'name': 'Engine Alignment', 'usl': 0.5, 'lsl': -0.5, 'target': 0},
            {'name': 'Paint Booth Temperature', 'usl': 25, 'lsl': 20, 'target': 22.5},
            {'name': 'Weld Penetration Depth', 'usl': 8, 'lsl': 6, 'target': 7}
        ]
        
        for process in processes:
            equipment = self.equipment_df.sample(1).iloc[0]
            
            # Generate 100 measurements per process
            # Vary the process capability
            sigma = (process['usl'] - process['lsl']) / (6 * random.uniform(1.2, 2.0))
            mean = process['target'] + random.uniform(-sigma, sigma)
            
            measurements = np.random.normal(mean, sigma, 100)
            
            records.append({
                'process_name': process['name'],
                'equipment_id': equipment['equipment_id'],
                'usl': process['usl'],
                'lsl': process['lsl'],
                'target': process['target'],
                'mean': round(np.mean(measurements), 3),
                'std_dev': round(np.std(measurements, ddof=1), 3),
                'measurements': ','.join([str(round(m, 2)) for m in measurements])
            })
        
        return pd.DataFrame(records)
    
    def calculate_dpmo_metrics(self, defect_df):
        """Calculate DPMO and Sigma level"""
        
        # Assume each equipment has 50 critical-to-quality characteristics
        opportunities_per_unit = 50
        total_units = len(self.equipment_df) * len(self.date_range) / 30  # Monthly production
        total_opportunities = total_units * opportunities_per_unit
        total_defects = len(defect_df)
        
        dpmo = (total_defects / total_opportunities) * 1_000_000
        
        # Convert DPMO to Sigma level (approximate)
        if dpmo < 3.4:
            sigma_level = 6.0
        elif dpmo < 233:
            sigma_level = 5.0
        elif dpmo < 6210:
            sigma_level = 4.0
        elif dpmo < 66807:
            sigma_level = 3.0
        else:
            sigma_level = 2.0
        
        return {
            'total_units': int(total_units),
            'opportunities_per_unit': opportunities_per_unit,
            'total_opportunities': int(total_opportunities),
            'total_defects': total_defects,
            'dpmo': round(dpmo, 2),
            'sigma_level': sigma_level,
            'yield_pct': round((1 - total_defects/total_opportunities) * 100, 2)
        }

    def generate_a3_report(self, defect_type):
        """
        Generate A3 Problem Solving Report data for a specific defect type
        """
        
        # Default report structure
        report = {
            'background': "Background analysis pending...",
            'current_condition': "Data collection in progress...",
            'goal': "Target not defined...",
            'root_cause': "Root cause analysis required...",
            'countermeasures': "Countermeasures to be identified...",
            'implementation': "Plan pending approval...",
            'follow_up': "Follow-up schedule tbd..."
        }
        
        if defect_type == 'Weld Defect' or defect_type == 'Weld Porosity':
            report = {
                'background': """<b>Context of the problem:</b><br>
Weld defects have increased by 15% in the last quarter, specifically porosity and lack of fusion in the hydraulic cylinder assembly line.<br>
This has resulted in increased rework costs ($12,000/month) and production delays (Avg 4 hours/week).""",
                
                'current_condition': f"""<b>Problem Statement:</b><br>
Current First Pass Yield for welding process is {random.uniform(88, 92):.1f}% (Target: 98%).<br>
Defect Rate: {random.randint(1200, 1500)} PPM.<br>
Primary Location: Station 4 (Robotic Welding Arm B).""",
                
                'goal': """<b>Specific metric targets:</b><br>
1. Reduce Weld Porosity defects by 50% within 3 months.<br>
2. Improve First Pass Yield to >96%.<br>
3. Reduce rework costs to <$5,000/month.""",
                
                'root_cause': """<b>5 Whys Analysis:</b><br>
1. Why? Porosity in weld bead. -> Gas coverage insufficient.<br>
2. Why? Gas flow interrupted. -> Nozzle clogged with spatter.<br>
3. Why? Auto-clean cycle not effective. -> Reamer blade worn out.<br>
4. Why? Preventive maintenance schedule missed. -> New operator not trained on PM.<br>
5. Why? Training matrix not updated. -> <b>Root Cause: Gap in Training Process & PM Standard Work.</b>""",
                
                'countermeasures': """<b>Proposed solutions:</b><br>
1. <b>Immediate:</b> Replace reamer blades and deep clean nozzle (Owner: Maintenance).<br>
2. <b>Systemic:</b> Implement auto-lockout if PM check is not logged (Owner: Engineering).<br>
3. <b>Process:</b> Update Standard Work for Operator PM training (Owner: Quality).""",
                
                'implementation': f"""<b>Who, When, What:</b><br>
- Maintenance Lead: Replace blades ({datetime.now().strftime('%Y-%m-%d')}) - <b>DONE</b><br>
- Shift Supervisor: Training Refresher (Due: {(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')})<br>
- Controls Eng: Update PLC logic for PM lockout (Due: {(datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')})""",
                
                'follow_up': f"""<b>Check results & standard work:</b><br>
- Audit weld quality daily for 30 days.<br>
- Review effective PM compliance weekly.<br>
- Target Date for Project Closure: {(datetime.now() + timedelta(days=45)).strftime('%Y-%m-%d')}"""
            }
        else:
            # Generic template for other defects
             report = {
                'background': f"""<b>Context of the problem:</b><br>
Increase in {defect_type} observed during final inspection.<br>
Impact: Customer complaints and increased warranty claims.""",
                
                'current_condition': f"""<b>Problem Statement:</b><br>
Defect rate for {defect_type} is currently above threshold.<br>
Observed frequency: {random.choice(['High', 'Medium', 'Increasing'])}.<br>
Affected Models: Series X, Series Y.""",
                
                'goal': f"""<b>Specific metric targets:</b><br>
1. Eliminate {defect_type} overflow to customer.<br>
2. Reduce internal occurrence by 40%.""",
                
                'root_cause': """<b>Potential Causes (Fishbone):</b><br>
- Man: Training / Standard Work<br>
- Machine: Calibration / Wear<br>
- Material: Supplier Variance<br>
- Method: Process Definition<br>
<i>Requires cross-functional investigation.</i>""",
                
                'countermeasures': """<b>Proposed solutions:</b><br>
1. Containment action to protect customer.<br>
2. Root cause verification trials.<br>
3. Permanent corrective action implementation.""",
                
                'implementation': """<b>Plan:</b><br>
- Phase 1: Investigation & Containment<br>
- Phase 2: Solution Implementation<br>
- Phase 3: Validation""",
                
                'follow_up': """<b>Validation:</b><br>
- Monitor quality metrics for 3 production runs.<br>
- Update FMEA and Control Plan."""
            }
            
        return report

def main():
    """Generate and save quality data"""
    
    print("Loading equipment data...")
    equipment = pd.read_csv('data/equipment.csv')
    
    print("Initializing Quality Data Generator...")
    generator = QualityDataGenerator(equipment)
    
    print("Generating SPC data...")
    spc_data = generator.generate_spc_data(num_samples=5000)
    spc_data.to_csv('data/quality_spc.csv', index=False)
    print(f"[SUCCESS] Generated {len(spc_data)} SPC inspection records")
    
    print("Generating defect data...")
    defect_data = generator.generate_defect_data(num_defects=2000)
    defect_data.to_csv('data/quality_defects.csv', index=False)
    print(f"[SUCCESS] Generated {len(defect_data)} defect records")
    
    print("Generating process capability data...")
    capability_data = generator.generate_process_capability_data()
    capability_data.to_csv('data/quality_capability.csv', index=False)
    print(f"[SUCCESS] Generated {len(capability_data)} process capability records")
    
    print("\nCalculating DPMO metrics...")
    dpmo_metrics = generator.calculate_dpmo_metrics(defect_data)
    print(f"  Total Units: {dpmo_metrics['total_units']:,}")
    print(f"  Total Defects: {dpmo_metrics['total_defects']:,}")
    print(f"  DPMO: {dpmo_metrics['dpmo']:,.2f}")
    print(f"  Sigma Level: {dpmo_metrics['sigma_level']}")
    print(f"  Yield: {dpmo_metrics['yield_pct']}%")
    
    print("\n[COMPLETE] Quality data generation complete!")

if __name__ == "__main__":
    main()
