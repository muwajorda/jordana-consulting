from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import sqlite3
import uuid
import json
from fastapi.middleware.cors import CORSMiddleware

DB = 'assessment_results.db'

app = FastAPI(title='Assessment API')
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Answers(BaseModel):
    organization_name: str
    organization_type: str
    employees: int
    cloud: str
    data_sources: List[str]
    it_team_size: int
    has_ai: bool

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS results (
        token TEXT PRIMARY KEY,
        payload TEXT,
        email TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

init_db()

def compute_score(a: Answers) -> Dict:
    # Simple heuristic scoring — replace with richer logic as needed
    base = 60
    breakdown = {
        'Infrastructure': 70,
        'Data': 55,
        'Cloud': 65,
        'AI': 40,
        'Security': 60,
        'Integration': 50
    }
    # adjustments
    if a.it_team_size < 5:
        base -= 5
        breakdown['Infrastructure'] -= 5
    if a.has_ai:
        base += 5
        breakdown['AI'] += 10
    if 'EHR' in [s.upper() for s in a.data_sources]:
        breakdown['Integration'] -= 5
        breakdown['Security'] += 3
    if a.cloud == 'none':
        base -= 5
        breakdown['Cloud'] = 30
    if a.employees > 500:
        base += 5
    score = max(0, min(100, base))
    return {'score': score, 'breakdown': breakdown}

@app.post('/api/assess')
def assess(answers: Answers):
    result = compute_score(answers)
    token = str(uuid.uuid4())
    payload = {
        'answers': answers.dict(),
        'readiness_score': result['score'],
        'breakdown': result['breakdown'],
        'top_priorities': ['Data Integration', 'AI Readiness', 'Cloud Optimization']
    }
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('INSERT INTO results(token,payload) VALUES (?,?)', (token, json.dumps(payload)))
    conn.commit()
    conn.close()
    return {'token': token, 'readiness_score': payload['readiness_score'], 'breakdown': payload['breakdown'], 'top_priorities': payload['top_priorities']}

@app.post('/api/claim/{token}')
def claim(token: str, body: Dict):
    # body should contain email
    email = body.get('email')
    if not email:
        raise HTTPException(status_code=400, detail='email required')
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('SELECT payload FROM results WHERE token=?', (token,))
    row = c.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail='token not found')
    c.execute('UPDATE results SET email=? WHERE token=?', (email, token))
    conn.commit()
    conn.close()
    return {'success': True}

@app.get('/api/result/{token}')
def get_result(token: str):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('SELECT payload,email,created_at FROM results WHERE token=?', (token,))
    row = c.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail='result not found')
    payload = json.loads(row[0])
    # if email is not set, do not return full report (only summary)
    email = row[1]
    if not email:
        # return limited fields
        return {
            'readiness_score': payload['readiness_score'],
            'breakdown': payload['breakdown'],
            'top_priorities': payload['top_priorities'],
            'claimed': False
        }
    payload['claimed'] = True
    return payload
