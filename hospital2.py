import argparse
import csv
import json
from dataclasses import dataclass, field
from collections import defaultdict
from datetime import datetime, date
from typing import List, Dict, Optional


# ---------------------- UTIL ----------------------

def parse_date(value):
    if not value:
        return None
    for fmt in ["%Y-%m-%d", "%d-%m-%Y"]:
        try:
            return datetime.strptime(value, fmt).date()
        except:
            continue
    return None


# ---------------------- DATA CLASSES ----------------------

@dataclass
class Patient:
    patient_id: str
    name: str
    age: int
    department: str
    doctor_id: str
    admission_date: Optional[date]
    discharge_date: Optional[date]
    consultation_fee: float
    room_charge: float
    diagnostic_fee: float
    surgery_fee: float
    insurance_coverage: float
    discount: float
    recovery_score: float
    accuracy_score: float
    critical: bool = False

    def total_bill(self):
        return round(
            self.consultation_fee +
            self.room_charge +
            self.diagnostic_fee +
            self.surgery_fee -
            self.insurance_coverage -
            self.discount,
            2
        )


@dataclass
class Doctor:
    doctor_id: str
    name: str
    department: str
    rating: float
    experience: int
    patients: List[str] = field(default_factory=list)


# ---------------------- LOADING DATA ----------------------

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def load_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def load_records(path):
    if not path:
        return []
    if path.endswith(".json"):
        return load_json(path)
    if path.endswith(".csv"):
        return load_csv(path)
    return []


# ---------------------- SAMPLE DATA ----------------------

def sample_data():
    patients = [
        Patient("P1", "Aarav", 50, "cardiology", "D1",
                parse_date("2026-03-01"), None,
                200, 500, 1000, 0, 300, 50, 75, 80, False),

        Patient("P2", "Divya", 40, "neurology", "D2",
                parse_date("2026-02-10"), parse_date("2026-02-20"),
                250, 300, 200, 0, 100, 20, 85, 90, False),

        Patient("P3", "Rohan", 65, "orthopedics", "D3",
                parse_date("2026-03-05"), None,
                400, 800, 2000, 5000, 2000, 100, 60, 55, True)
    ]

    doctors = {
        "D1": Doctor("D1", "Dr Meera", "cardiology", 4.8, 15),
        "D2": Doctor("D2", "Dr Patel", "neurology", 4.9, 12),
        "D3": Doctor("D3", "Dr Anjali", "orthopedics", 4.5, 10),
    }

    return patients, doctors


# ---------------------- CORE SYSTEM ----------------------

class HospitalSystem:

    def __init__(self, patients: List[Patient], doctors: Dict[str, Doctor]):
        self.patients = patients
        self.doctors = doctors

    # 🔹 assign patients to doctors
    def map_doctors(self):
        for d in self.doctors.values():
            d.patients.clear()

        for p in self.patients:
            if p.doctor_id in self.doctors:
                self.doctors[p.doctor_id].patients.append(p.patient_id)

    # 🔹 top doctors
    def top_doctors(self):
        self.map_doctors()
        return sorted(
            self.doctors.values(),
            key=lambda d: (d.rating, len(d.patients), d.experience),
            reverse=True
        )

    # 🔹 revenue
    def revenue_by_department(self):
        rev = defaultdict(float)
        for p in self.patients:
            rev[p.department] += p.total_bill()
        return rev

    # 🔹 discharge candidates
    def discharge_list(self):
        return [
            p for p in self.patients
            if p.recovery_score >= 70 and p.accuracy_score >= 65 and not p.discharge_date
        ]

    # 🔹 anomalies
    def billing_anomalies(self):
        issues = {}
        for p in self.patients:
            if p.total_bill() < 0:
                issues[p.patient_id] = "Negative bill"
            if p.diagnostic_fee > 3000:
                issues[p.patient_id] = "High diagnostic fee"
        return issues

    # 🔹 critical patients
    def critical_patients(self):
        scored = []
        for p in self.patients:
            risk = (100 - p.recovery_score) + (100 - p.accuracy_score) * 0.5
            if p.critical:
                risk += 10
            scored.append((risk, p))
        return [p for _, p in sorted(scored, reverse=True)[:5]]


# ---------------------- REPORT ----------------------

def print_report(system: HospitalSystem):

    print("\n✅ TOP DOCTORS")
    for d in system.top_doctors():
        print(f"{d.name} | Rating: {d.rating} | Patients: {len(d.patients)}")

    print("\n💰 REVENUE BY DEPARTMENT")
    for k, v in system.revenue_by_department().items():
        print(f"{k}: ₹{v}")

    print("\n🏥 DISCHARGE LIST")
    for p in system.discharge_list():
        print(p.patient_id, p.name)

    print("\n⚠ BILLING ISSUES")
    for k, v in system.billing_anomalies().items():
        print(k, "->", v)

    print("\n🚨 CRITICAL PATIENTS")
    for p in system.critical_patients():
        print(p.patient_id, p.name)


# ---------------------- MAIN ----------------------

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--patients-file")
    parser.add_argument("--doctors-file")
    return parser.parse_args()


def main():
    print("Program Started...\n")

    args = parse_arguments()

    raw_p = load_records(args.patients_file)
    raw_d = load_records(args.doctors_file)

    if not raw_p:
        print("Using Sample Data...\n")
        patients, doctors = sample_data()
    else:
        print("File loading version not implemented fully yet.")
        return

    system = HospitalSystem(patients, doctors)

    print_report(system)


# ---------------------- RUN ----------------------

if __name__ == "__main__":
    main()