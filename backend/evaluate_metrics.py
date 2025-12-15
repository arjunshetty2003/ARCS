import requests
import pandas as pd
import glob

# Configuration
API_URL = "http://localhost:8000/generate-schedule"

def load_data(data_dir):
    """Load the CSV data for validation."""
    try:
        students = pd.read_csv(f"{data_dir}/students.csv")
        teachers = pd.read_csv(f"{data_dir}/teachers.csv")
        slots = pd.read_csv(f"{data_dir}/slots.csv")
        busy = pd.read_csv(f"{data_dir}/busy.csv")
        return students, teachers, slots, busy
    except FileNotFoundError as e:
        print(f"Error loading test data from {data_dir}: {e}")
        raise e

def get_schedule(data_dir):
    """Call the backend API to generate the schedule."""
    files = {
        'students': open(f'{data_dir}/students.csv', 'rb'),
        'teachers': open(f'{data_dir}/teachers.csv', 'rb'),
        'slots': open(f'{data_dir}/slots.csv', 'rb'),
        'busy': open(f'{data_dir}/busy.csv', 'rb'),
    }
    
    print(f"Requesting schedule for {data_dir} from Gemini API...")
    try:
        response = requests.post(API_URL, files=files, timeout=600)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API Request failed: {e}")
        return None

def calculate_metrics(schedule, df_students, df_teachers, df_slots, df_busy):
    print("\nEvaluating Schedule...")
    
    # 1. Intent Recall (Demand Coverage)
    failing_students = df_students[df_students['Score'] < 40]
    total_failing = len(failing_students)
    scheduled_students = set(item['Student Name'] for item in schedule)
    failing_student_names = set(failing_students['Name'])
    
    # Intersection of scheduled vs actual failing students
    unique_scheduled = len(scheduled_students.intersection(failing_student_names))
    
    recall = (unique_scheduled / total_failing) * 100 if total_failing > 0 else 0

    # 2. Hallucination Rate
    fake_ids_count = 0
    total_ids_checked = 0
    
    valid_students = set(df_students['Name'])
    valid_teachers = set(df_teachers['Name'])
    valid_slots = set(df_slots['Slot_ID'].astype(str)) # Ensure string comparison
    
    for item in schedule:
        # Check Student
        total_ids_checked += 1
        if item['Student Name'] not in valid_students:
            fake_ids_count += 1
            print(f"Hallucination Found: Unknown Student '{item['Student Name']}'")

        # Check Teacher
        total_ids_checked += 1
        if item['Teacher Name'] not in valid_teachers:
            fake_ids_count += 1
            print(f"Hallucination Found: Unknown Teacher '{item['Teacher Name']}'")
            
        # Check Slot (Backend output includes real time, but Slot_ID is key)
        total_ids_checked += 1
        if str(item['Slot_ID']) not in valid_slots:
            fake_ids_count += 1
            print(f"Hallucination Found: Unknown Slot ID '{item['Slot_ID']}'")

    hallucination_rate = (fake_ids_count / total_ids_checked) * 100 if total_ids_checked > 0 else 0

    # 3. Constraint Satisfaction Rate (CSR)
    violations = 0
    total_assignments = len(schedule)
    
    # Create lookups
    student_section_map = dict(zip(df_students['Name'], df_students['Section']))
    busy_map = {} # Section -> Set of Busy Slot IDs
    for _, row in df_busy.iterrows():
        busy_map[row['Section']] = set(str(row['Busy_Slot_IDs']).split(';'))
        
    teacher_slots_map = {} # Name -> Set of Free Slot IDs
    for _, row in df_teachers.iterrows():
        teacher_slots_map[row['Name']] = set(str(row['Slot_IDs']).split(';'))

    for item in schedule:
        is_valid = True
        student = item['Student Name']
        teacher = item['Teacher Name']
        slot = str(item['Slot_ID'])
        
        # Rule 1: Student Busy?
        section = student_section_map.get(student)
        if section and section in busy_map:
            if slot in busy_map[section]:
                print(f"Constraint Violation: {student} ({section}) is busy at {slot}")
                is_valid = False
        
        # Rule 2: Teacher Free?
        if teacher in teacher_slots_map:
            if slot not in teacher_slots_map[teacher]:
                print(f"Constraint Violation: {teacher} is NOT free at {slot}")
                is_valid = False
        
        if not is_valid:
            violations += 1

    valid_classes = total_assignments - violations
    csr = (valid_classes / total_assignments) * 100 if total_assignments > 0 else 0

    return {
        "CSR": csr,
        "Hallucination Rate": hallucination_rate,
        "Intent Recall": recall,
        "Total Assignments": total_assignments,
        "Total Failing": total_failing,
        "Scheduled Unique": unique_scheduled,
        "Violations": violations,
        "Fake IDs": fake_ids_count
    }

def print_report(metrics):
    print("\n" + "="*40)
    print(f"      EVALUATION REPORT FOR {metrics.get('Dataset', 'DATA').upper()}      ")
    print("="*40)
    
    print(f"\n1. CONSTRAINT SATISFACTION RATE (CSR)")
    print(f"   Score: {metrics['CSR']:.2f}%")
    print(f"   (Valid Assignments: {metrics['Total Assignments'] - metrics['Violations']}/{metrics['Total Assignments']})")
    
    print(f"\n2. HALLUCINATION RATE")
    print(f"   Score: {metrics['Hallucination Rate']:.2f}%")
    print(f"   (Fake Data Points: {metrics['Fake IDs']})")
    
    print(f"\n3. INTENT RECALL (Demand Coverage)")
    print(f"   Score: {metrics['Intent Recall']:.2f}%")
    print(f"   (Students Scheduled: {metrics['Scheduled Unique']}/{metrics['Total Failing']})")
    
    print("\n" + "="*40)
    if metrics['CSR'] == 100 and metrics['Hallucination Rate'] == 0 and metrics['Intent Recall'] >= 90:
        print("RESULT: EXCELLENT (Production Ready)")
    elif metrics['CSR'] >= 90:
        print("RESULT: GOOD (Minor Tuning Needed)")
    else:
        print("RESULT: FAIL (Prompt/Model Logic Failed)")
    print("="*40 + "\n")

if __name__ == "__main__":
    datasets = ["test_data", "large_test_data", "stress_test_data"]
    
    for dataset in datasets:
        print(f"\n{'#'*40}")
        print(f"RUNNING EVALUATION ON: {dataset}")
        print(f"{'#'*40}")
        
        try:
            df_students, df_teachers, df_slots, df_busy = load_data(dataset)
            schedule = get_schedule(dataset)
            
            if not schedule:
                print(f"No schedule generated for {dataset}.")
            else:
                metrics = calculate_metrics(schedule, df_students, df_teachers, df_slots, df_busy)
                metrics['Dataset'] = dataset
                print_report(metrics)
        except Exception as e:
            print(f"Failed to evaluate {dataset}: {e}")
