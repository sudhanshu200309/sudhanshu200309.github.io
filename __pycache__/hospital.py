import csv
import json
import os
import argparse
from collections import defaultdict

# ===================== CUSTOM EXCEPTIONS =====================
class BillingDataError(Exception):
    pass

class DuplicatePatientError(Exception):
    pass

class InsuranceCalculationError(Exception):
    pass


# ===================== PATIENT CLASS =====================
class Patient:
    def __init__(self, **data):
        self.pid = data["pid"]
        self.name = data["name"]
        self.age = int(data["age"])
        self.department = data["department"]
        self.doctor_id = data["doctor_id"]

        if not self.doctor_id:
            raise ValueError(f"Missing doctor for patient {self.pid}")

        self.admission_date = data["admission_date"]
        self.discharge_status = data["discharge_status"]

        self.room_charge = float(data["room_charge"])
        self.diagnostic_fee = float(data["diagnostic_fee"])
        self.surgery_cost = float(data["surgery_cost"])
        self.insurance_coverage = float(data["insurance_coverage"])
        self.discount = float(data["discount"])


# ===================== DOCTOR CLASS =====================
class Doctor:
    def __init__(self, **data):
        self.did = data["did"]
        self.name = data["name"]
        self.department = data["department"]
        self.rating = float(data["rating"])
        self.recovery_score = float(data["recovery_score"])
        self.punctuality = float(data["punctuality"])
        self.accuracy = float(data["accuracy"])

    def overall_score(self):
        return (self.rating + self.recovery_score +
                self.punctuality + self.accuracy) / 4


# ===================== BILLING ENGINE =====================
class BillingEngine:
    CONSULTATION_FEE = 500

    def calculate_bill(self, p):
        total = (self.CONSULTATION_FEE + p.room_charge + p.diagnostic_fee +
                 p.surgery_cost - p.insurance_coverage - p.discount)

        if total < 0:
            raise BillingDataError(f"Negative bill for {p.pid}")

        return total

    def detect_anomalies(self, p, total):
        issues = []

        if total < 0:
            issues.append("Negative Bill")

        if p.diagnostic_fee > 50000:
            issues.append("High Diagnostic Fee")

        if p.insurance_coverage > (
            p.room_charge + p.diagnostic_fee + p.surgery_cost
        ):
            issues.append("Invalid Insurance Claim")

        if p.discharge_status == "YES" and p.room_charge > 25000:
            issues.append("Overcharged Room After Discharge")

        return issues


# ===================== FILE CREATION =====================
def create_sample_files():
    if not os.path.exists("patients.csv"):
        print("⚠ Creating sample patients.csv")

        with open("patients.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "pid", "name", "age", "department", "doctor_id",
                "admission_date", "discharge_status", "room_charge",
                "diagnostic_fee", "surgery_cost", "insurance_coverage", "discount"
            ])
            writer.writerows([
                ["P1", "Ravi", 45, "Cardiology", "D1", "2024-01-01", "NO", 20000, 5000, 0, 3000, 1000],
                ["P2", "Anita", 70, "Neurology", "D2", "2024-01-02", "YES", 30000, 70000, 10000, 5000, 2000],
                ["P3", "Rahul", 30, "Orthopedics", "D3", "2024-02-01", "NO", 15000, 3000, 0, 2000, 500],
            ])

    if not os.path.exists("doctors.csv"):
        print("⚠ Creating sample doctors.csv")

        with open("doctors.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "did", "name", "department", "rating",
                "recovery_score", "punctuality", "accuracy"
            ])
            writer.writerows([
                ["D1", "Dr.Sharma", "Cardiology", 9, 8, 9, 8],
                ["D2", "Dr.Rao", "Neurology", 8, 9, 7, 9],
                ["D3", "Dr.Kumar", "Orthopedics", 7, 8, 8, 7],
            ])


# ===================== LOAD DATA =====================
def load_patients(file):
    patients = []
    ids = set()

    with open(file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["pid"] in ids:
                raise DuplicatePatientError("Duplicate Patient ID")
            ids.add(row["pid"])

            try:
                patients.append(Patient(**row))
            except Exception as e:
                print(f"⚠ Skipping patient error: {e}")

    return patients


def load_doctors(file):
    doctors = []
    with open(file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            doctors.append(Doctor(**row))
    return doctors


# ===================== REPORT SYSTEM =====================
class HospitalReportSystem:
    def __init__(self, patients, doctors, billing):
        self.patients = patients
        self.doctors = doctors
        self.billing = billing

    def top_doctors(self):
        return sorted(self.doctors,
                      key=lambda d: d.overall_score(),
                      reverse=True)[:10]

    def revenue_by_department(self):
        revenue = defaultdict(float)
        for p in self.patients:
            try:
                bill = self.billing.calculate_bill(p)
                revenue[p.department] += bill
            except:
                pass
        return revenue

    def discharge_candidates(self):
        return [p for p in self.patients if p.discharge_status == "NO"]

    def anomalies(self):
        result = []
        for p in self.patients:
            try:
                bill = self.billing.calculate_bill(p)
                issues = self.billing.detect_anomalies(p, bill)
                if issues:
                    result.append((p.pid, issues))
            except Exception as e:
                result.append((p.pid, str(e)))
        return result

    def critical_patients(self):
        return [p for p in self.patients if p.age > 65]


# ===================== RECURSION =====================
def traverse_dept(tree, node="Hospital", level=0):
    print("  " * level + node)
    for child in tree.get(node, []):
        traverse_dept(tree, child, level + 1)


# ===================== CLI MAIN =====================
def main():
    # Step 1: Ensure files exist
    create_sample_files()

    # Step 2: CLI
    parser = argparse.ArgumentParser()
    parser.add_argument("--month", default="march")
    parser.add_argument("--department", default="all")
    args = parser.parse_args()

    print("\n📁 Working Directory:", os.getcwd())

    # Step 3: Load data
    try:
        patients = load_patients("patients.csv")
        doctors = load_doctors("doctors.csv")
    except Exception as e:
        print("❌ Error loading files:", e)
        return

    billing = BillingEngine()
    report = HospitalReportSystem(patients, doctors, billing)

    # ===================== OUTPUT =====================
    print("\n🏆 Top Doctors:")
    for d in report.top_doctors():
        print(d.name, "→ Score:", round(d.overall_score(), 2))

    print("\n💰 Revenue by Department:")
    print(dict(report.revenue_by_department()))

    print("\n⚠ Billing Anomalies:")
    for a in report.anomalies():
        print(a)

    print("\n🚑 Critical Patients (>65):")
    for p in report.critical_patients():
        print(p.name)

    print("\n🛏 Patients Eligible for Discharge:")
    for p in report.discharge_candidates():
        print(p.name)

    print("\n🏥 Department Tree:")
    dept_tree = {
        "Hospital": ["Cardiology", "Neurology"],
        "Cardiology": ["ICU", "General Ward"],
        "Neurology": ["ICU"]
    }
    traverse_dept(dept_tree)


# ===================== RUN =====================
if __name__ == "__main__":
    main()