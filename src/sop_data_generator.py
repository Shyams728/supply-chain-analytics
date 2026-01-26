"""
SOP Data Generator
Generates realistic synthetic data for SOP management system testing

Author: Shyamsundar Dharwad
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# ============================================================================
# CONFIGURATION
# ============================================================================

NUM_SOPS = 50
NUM_EXECUTIONS_PER_SOP = (10, 50)  # Range
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2025, 12, 31)

# ============================================================================
# REFERENCE DATA
# ============================================================================

SOP_CATEGORIES = ['Maintenance', 'Safety', 'Quality', 'Inventory', 'Logistics', 'Operations']

MAINTENANCE_SOPS = [
    'Hydraulic Pump Replacement',
    'Engine Oil Change',
    'Brake System Inspection',
    'Transmission Service',
    'Cooling System Maintenance',
    'Track Adjustment Procedure',
    'Electrical System Diagnostics',
    'Fuel System Cleaning',
    'Air Filter Replacement',
    'Undercarriage Inspection'
]

SAFETY_SOPS = [
    'Lockout/Tagout Procedure',
    'Fall Protection Inspection',
    'Fire Extinguisher Check',
    'Emergency Shutdown Protocol',
    'PPE Inspection Standards',
    'Confined Space Entry',
    'Hot Work Permit Process',
    'Hazard Communication'
]

QUALITY_SOPS = [
    'Final Inspection Checklist',
    'Weld Quality Verification',
    'Torque Specification Compliance',
    'Dimensional Inspection',
    'Paint Quality Check',
    'Assembly Verification'
]

INVENTORY_SOPS = [
    'Parts Receiving Procedure',
    'Cycle Count Process',
    'Stock Issuance Protocol',
    'Obsolete Parts Disposal',
    'Inventory Reconciliation'
]

LOGISTICS_SOPS = [
    'Material Handling Safety',
    'Loading/Unloading Procedure',
    'Shipping Documentation',
    'Delivery Route Planning'
]

OPERATIONS_SOPS = [
    'Work Order Processing',
    'Equipment Handover Protocol',
    'Shift Changeover Procedure',
    'Incident Reporting'
]

SOP_TEMPLATES = {
    'Maintenance': MAINTENANCE_SOPS,
    'Safety': SAFETY_SOPS,
    'Quality': QUALITY_SOPS,
    'Inventory': INVENTORY_SOPS,
    'Logistics': LOGISTICS_SOPS,
    'Operations': OPERATIONS_SOPS
}

DEPARTMENTS = ['Maintenance', 'Safety', 'Quality', 'Logistics', 'Operations', 'Engineering']
TECHNICIANS = [
    'John Smith', 'Mike Johnson', 'Sarah Williams', 'David Brown',
    'Lisa Garcia', 'Robert Martinez', 'Jennifer Davis', 'William Rodriguez',
    'Mary Wilson', 'James Anderson', 'Patricia Taylor', 'Christopher Thomas'
]

COMPETENCY_LEVELS = ['Basic', 'Intermediate', 'Expert']
COMPLIANCE_STATUSES = ['Fully Compliant', 'Partial Compliance', 'Non-Compliant']

# ============================================================================
# DATA GENERATION FUNCTIONS
# ============================================================================

def generate_sop_master():
    """Generate SOP master data"""
    sops = []
    sop_id_counter = 1
    
    for category, sop_titles in SOP_TEMPLATES.items():
        for title in sop_titles:
            version = '1.0' if random.random() > 0.3 else random.choice(['1.1', '2.0', '1.2'])
            
            created_date = START_DATE + timedelta(
                days=random.randint(0, (END_DATE - START_DATE).days // 2)
            )
            
            # Most SOPs are active, some are draft or archived
            status_prob = random.random()
            if status_prob > 0.85:
                status = 'Draft'
                effective_date = None
                review_date = None
            elif status_prob > 0.75:
                status = 'Archived'
                effective_date = created_date + timedelta(days=30)
                review_date = effective_date + timedelta(days=365)
            else:
                status = 'Active'
                effective_date = created_date + timedelta(days=30)
                review_date = effective_date + timedelta(days=365)
            
            sop = {
                'sop_id': f'SOP-{category[:4].upper()}-{sop_id_counter:04d}',
                'sop_title': title,
                'sop_category': category,
                'version': version,
                'status': status,
                'effective_date': effective_date,
                'review_date': review_date,
                'owner_department': random.choice(DEPARTMENTS),
                'approval_authority': random.choice(['Chief Engineer', 'Safety Manager', 
                                                    'Operations Director', 'Quality Manager']),
                'created_by': random.choice(TECHNICIANS),
                'created_date': created_date,
                'last_modified_by': random.choice(TECHNICIANS) if random.random() > 0.5 else None,
                'last_modified_date': created_date + timedelta(days=random.randint(10, 100)) 
                                     if random.random() > 0.5 else None,
                'file_path': f'/sops/{category.lower()}/{title.lower().replace(" ", "_")}.pdf',
                'description': f'Standard operating procedure for {title.lower()}'
            }
            
            sops.append(sop)
            sop_id_counter += 1
    
    return pd.DataFrame(sops)

def generate_sop_steps(sop_master_df):
    """Generate SOP steps for each SOP"""
    steps = []
    
    for _, sop in sop_master_df.iterrows():
        # Each SOP has 3-8 steps
        num_steps = random.randint(3, 8)
        
        for step_num in range(1, num_steps + 1):
            step = {
                'step_id': f"{sop['sop_id']}-STEP{step_num:03d}",
                'sop_id': sop['sop_id'],
                'step_number': step_num,
                'step_title': f"Step {step_num}: {random.choice(['Prepare', 'Execute', 'Verify', 'Document', 'Inspect', 'Clean', 'Assemble', 'Test'])} {random.choice(['Equipment', 'Tools', 'Area', 'Components', 'System', 'Parts'])}",
                'step_description': f'Detailed procedure for step {step_num} of {sop["sop_title"]}',
                'estimated_duration_minutes': random.choice([10, 15, 20, 30, 45, 60, 90]),
                'required_competency_level': random.choice(COMPETENCY_LEVELS),
                'safety_critical': random.random() > 0.7,  # 30% are safety critical
                'quality_checkpoint': random.random() > 0.6,  # 40% have quality checks
                'tools_required': random.choice([
                    'Socket set, Torque wrench',
                    'Multimeter, Wire strippers',
                    'Hydraulic pressure gauge',
                    'Micrometers, Calipers',
                    'None',
                    'Standard tool kit'
                ]),
                'consumables_required': random.choice([
                    'Oil filter, Engine oil',
                    'Gaskets, Sealant',
                    'Hydraulic fluid',
                    'None',
                    'Cleaning supplies',
                    'Fasteners'
                ]),
                'predecessor_step': f"{sop['sop_id']}-STEP{step_num-1:03d}" if step_num > 1 else None,
                'acceptance_criteria': 'Visual inspection passes' if random.random() > 0.5 else 'Measurement within tolerance'
            }
            
            steps.append(step)
    
    return pd.DataFrame(steps)

def generate_sop_executions(sop_master_df, sop_steps_df):
    """Generate SOP execution records"""
    executions = []
    execution_id = 1
    
    # Only generate executions for active SOPs
    active_sops = sop_master_df[sop_master_df['status'] == 'Active']
    
    for _, sop in active_sops.iterrows():
        # Number of times this SOP was executed
        num_executions = random.randint(*NUM_EXECUTIONS_PER_SOP)
        
        for _ in range(num_executions):
            start_time = START_DATE + timedelta(
                days=random.randint(0, (END_DATE - START_DATE).days)
            )
            
            # Ensure start time is after SOP effective date
            if pd.notna(sop['effective_date']):
                effective = pd.to_datetime(sop['effective_date'])
                if start_time < effective:
                    start_time = effective + timedelta(days=random.randint(1, 30))
            
            # Get expected duration from steps
            sop_steps = sop_steps_df[sop_steps_df['sop_id'] == sop['sop_id']]
            expected_duration = sop_steps['estimated_duration_minutes'].sum()
            
            # Actual duration varies ±30%
            actual_duration = expected_duration * random.uniform(0.7, 1.3)
            end_time = start_time + timedelta(minutes=actual_duration)
            
            # Compliance status (80% fully compliant, 15% partial, 5% non-compliant)
            compliance_rand = random.random()
            if compliance_rand > 0.95:
                compliance_status = 'Non-Compliant'
                deviations = random.choice([
                    'Step 3 skipped due to time constraints',
                    'Tools not available, used alternative method',
                    'Safety check not performed',
                    'Incorrect torque specification used'
                ])
            elif compliance_rand > 0.80:
                compliance_status = 'Partial Compliance'
                deviations = random.choice([
                    'Step sequence modified',
                    'Alternative material used',
                    'Quality check delayed'
                ])
            else:
                compliance_status = 'Fully Compliant'
                deviations = ''
            
            execution = {
                'execution_id': f'EXEC{execution_id:06d}',
                'sop_id': sop['sop_id'],
                'work_order_id': f'WO{random.randint(10000, 99999)}',
                'equipment_id': f'EQ{random.randint(1, 50):04d}',
                'executed_by': random.choice(TECHNICIANS),
                'start_time': start_time,
                'end_time': end_time,
                'duration_minutes': round(actual_duration, 1),
                'compliance_status': compliance_status,
                'deviations_noted': deviations,
                'comments': random.choice(['Completed successfully', 'No issues', 'Minor delays', '']),
                'supervisor_verified': random.random() > 0.2  # 80% verified
            }
            
            executions.append(execution)
            execution_id += 1
    
    return pd.DataFrame(executions)

def generate_step_completions(execution_df, sop_steps_df):
    """Generate step completion records for each execution"""
    completions = []
    completion_id = 1
    
    for _, execution in execution_df.iterrows():
        # Get steps for this SOP
        steps = sop_steps_df[sop_steps_df['sop_id'] == execution['sop_id']].sort_values('step_number')
        
        current_time = execution['start_time']
        
        for _, step in steps.iterrows():
            # Most steps are completed (95%)
            completed = random.random() > 0.05
            
            # Add step duration
            current_time = current_time + timedelta(
                minutes=step['estimated_duration_minutes'] * random.uniform(0.8, 1.2)
            )
            
            # Deviations are rare (10%)
            deviation = random.random() > 0.90
            deviation_reason = ''
            
            if deviation:
                deviation_reason = random.choice([
                    'Tool not available',
                    'Part substitution required',
                    'Sequence modified for efficiency',
                    'Safety concern - alternate method used',
                    'Quality issue detected - rework needed'
                ])
            
            # Quality checks mostly pass (95%)
            quality_passed = random.random() > 0.05 if step['quality_checkpoint'] else True
            
            completion = {
                'completion_id': f'COMP{completion_id:07d}',
                'execution_id': execution['execution_id'],
                'step_id': step['step_id'],
                'completed': completed,
                'completion_time': current_time if completed else None,
                'deviation_from_sop': deviation,
                'deviation_reason': deviation_reason,
                'quality_check_passed': quality_passed
            }
            
            completions.append(completion)
            completion_id += 1
    
    return pd.DataFrame(completions)

# ============================================================================
# MAIN GENERATION FUNCTION
# ============================================================================

def generate_all_sop_data(output_dir='data/'):
    """Generate complete SOP dataset"""
    print("Generating SOP Data...")
    print("=" * 70)
    
    # 1. Generate SOP Master
    print("1. Generating SOP Master data...")
    sop_master = generate_sop_master()
    print(f"   ✓ Generated {len(sop_master)} SOPs")
    
    # 2. Generate SOP Steps
    print("2. Generating SOP Steps...")
    sop_steps = generate_sop_steps(sop_master)
    print(f"   ✓ Generated {len(sop_steps)} steps")
    
    # 3. Generate Executions
    print("3. Generating SOP Executions...")
    executions = generate_sop_executions(sop_master, sop_steps)
    print(f"   ✓ Generated {len(executions)} executions")
    
    # 4. Generate Step Completions
    print("4. Generating Step Completions...")
    step_completions = generate_step_completions(executions, sop_steps)
    print(f"   ✓ Generated {len(step_completions)} step completions")
    
    # Save to CSV
    print("\n5. Saving data to CSV files...")
    sop_master.to_csv(f'{output_dir}sop_master.csv', index=False)
    print(f"   ✓ Saved {output_dir}sop_master.csv")
    
    sop_steps.to_csv(f'{output_dir}sop_steps.csv', index=False)
    print(f"   ✓ Saved {output_dir}sop_steps.csv")
    
    executions.to_csv(f'{output_dir}sop_execution_log.csv', index=False)
    print(f"   ✓ Saved {output_dir}sop_execution_log.csv")
    
    step_completions.to_csv(f'{output_dir}sop_step_completion.csv', index=False)
    print(f"   ✓ Saved {output_dir}sop_step_completion.csv")
    
    # Summary statistics
    print("\n" + "=" * 70)
    print("DATA GENERATION SUMMARY")
    print("=" * 70)
    print(f"Total SOPs:               {len(sop_master)}")
    print(f"Active SOPs:              {len(sop_master[sop_master['status'] == 'Active'])}")
    print(f"Total Steps:              {len(sop_steps)}")
    print(f"Total Executions:         {len(executions)}")
    print(f"Total Step Completions:   {len(step_completions)}")
    print(f"\nCompliance Breakdown:")
    print(executions['compliance_status'].value_counts())
    print(f"\nSOP Category Breakdown:")
    print(sop_master['sop_category'].value_counts())
    print("=" * 70)
    
    return {
        'sop_master': sop_master,
        'sop_steps': sop_steps,
        'executions': executions,
        'step_completions': step_completions
    }

# ============================================================================
# RUN GENERATOR
# ============================================================================

if __name__ == "__main__":
    import os
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Generate all data
    data = generate_all_sop_data()
    
    print("\n✓ SOP data generation complete!")
    print("\nFiles created:")
    print("  - data/sop_master.csv")
    print("  - data/sop_steps.csv")
    print("  - data/sop_execution_log.csv")
    print("  - data/sop_step_completion.csv")
    print("\nYou can now use these files with the SOP Manager!")