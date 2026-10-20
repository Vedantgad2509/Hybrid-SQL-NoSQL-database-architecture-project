"""Synthetic hospital data generator. Usage: python generate_data.py --n 10000 --out data_10k"""
import argparse, csv, json, os, random
from faker import Faker
p = argparse.ArgumentParser(); p.add_argument('--n', type=int, default=10000); p.add_argument('--out', default='data')
a = p.parse_args(); os.makedirs(a.out, exist_ok=True)
fake = Faker(); Faker.seed(42); random.seed(42)
N_DOC = max(10, a.n // 100)

def w_csv(name, header, rows):
    with open(f'{a.out}/{name}.csv', 'w', newline='', encoding='utf-8') as f:
        wr = csv.writer(f); wr.writerow(header); wr.writerows(rows)

w_csv('doctors', ['doctor_id','name','specialty'],
      [(d, fake.name(), random.choice(['Cardiology','Neurology','Orthopedics','General','Pediatrics'])) for d in range(1, N_DOC+1)])
w_csv('patients', ['patient_id','name','dob','gender','phone'],
      [(i, fake.name(), fake.date_of_birth(minimum_age=1, maximum_age=90), random.choice('MF'), fake.phone_number()) for i in range(1, a.n+1)])
w_csv('appointments', ['appt_id','patient_id','doctor_id','appt_date','status'],
      [(i, i, random.randint(1, N_DOC), fake.date_this_year(), random.choice(['done','scheduled','cancelled'])) for i in range(1, a.n+1)])
w_csv('billing', ['bill_id','patient_id','amount','paid'],
      [(i, i, round(random.uniform(200, 20000), 2), random.choice([True, False])) for i in range(1, a.n+1)])

def vitals(pid):  # fields vary by monitoring device
    dev = random.choice(['ecg','pulse_ox','bp_cuff'])
    d = {'patient_id': pid, 'device': dev, 'ts': fake.date_time_this_month().isoformat()}
    if dev == 'ecg': d.update(heart_rate=random.randint(50,120), qrs_ms=random.randint(70,120))
    elif dev == 'pulse_ox': d.update(spo2=random.randint(88,100), pulse=random.randint(50,120))
    else: d.update(systolic=random.randint(95,170), diastolic=random.randint(60,105))
    return d

def lab(pid):  # schema varies by test type
    t = random.choice(['blood_panel','imaging','pathology'])
    d = {'patient_id': pid, 'test_type': t}
    if t == 'blood_panel': d['results'] = {'hb': round(random.uniform(8,17),1), 'wbc': random.randint(3000,12000), 'platelets': random.randint(120,420)}
    elif t == 'imaging': d['results'] = {'modality': random.choice(['xray','ct','mri']), 'finding': fake.sentence(), 'image_ref': fake.uuid4()}
    else: d['results'] = {'specimen': random.choice(['biopsy','smear']), 'grade': random.randint(1,4), 'report': fake.paragraph()}
    return d

with open(f'{a.out}/vitals.jsonl','w') as fv, open(f'{a.out}/labs.jsonl','w') as fl, open(f'{a.out}/notes.jsonl','w') as fn:
    for pid in range(1, a.n+1):
        for _ in range(10): fv.write(json.dumps(vitals(pid))+'\n')
        fl.write(json.dumps(lab(pid))+'\n')
        fn.write(json.dumps({'patient_id': pid, 'doctor_id': random.randint(1,N_DOC), 'note': fake.paragraph(), 'tags': random.sample(['follow-up','urgent','allergy','chronic','discharge'], 2)})+'\n')
print('done', a.n, 'patients ->', a.out)