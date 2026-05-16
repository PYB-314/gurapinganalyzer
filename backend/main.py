from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
import os
import json

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
class AnalysisRequest(BaseModel):
    text: str
    mode: str

class DetailRequest(BaseModel):
    text: str
    propositions: list[str]

SYSTEM_PROMPT = """
당신은 논리 분석 엔진입니다. 반드시 아래 JSON 형식으로만 응답하세요. 설명체 문장 금지.

{
  "propositions": ["명제1", "명제2"],
  "verdict": "참" 또는 "거짓" 또는 "판단불가",
  "reason": "근거 1~2문장",
  "counterexample": "반례 내용 또는 null",
  "logic_structure": {
    "premises": ["전제1", "전제2"],
    "conclusion": "결론"
  }
}
"""

DETAIL_PROMPT = """
당신은 논리 분석 엔진입니다. 반드시 아래 JSON 형식으로만 응답하세요. 설명체 문장 금지.

각 명제에 대해 역과 대우를 만들고 참/거짓을 판별하세요.

{
  "detailed_analysis": [
    {
      "proposition": "원래 명제",
      "converse": "역 명제",
      "contrapositive": "대우 명제",
      "original_verdict": "참 또는 거짓",
      "converse_verdict": "참 또는 거짓",
      "contrapositive_verdict": "참 또는 거짓",
      "explanation": "판별 근거 설명"
    }
  ],
  "overall_conclusion": "종합 결론 1~2문장"
}
"""

@app.post("/analyze")
async def analyze(req: AnalysisRequest):
    if req.mode == "news":
        user_prompt = f"다음 텍스트에서 명제를 추출하고 각 명제의 참/거짓과 반례를 분석하세요:\n\n{req.text}"
    else:
        user_prompt = f"다음 논증의 전제와 결론을 파악하고 반례를 분석하세요:\n\n{req.text}"

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        max_tokens=1024,
    )

    result = json.loads(response.choices[0].message.content)
    return result

@app.post("/analyze-detail")
async def analyze_detail(req: DetailRequest):
    user_prompt = f"원본 텍스트:\n{req.text}\n\n추출된 명제들:\n" + "\n".join(req.propositions)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": DETAIL_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        max_tokens=2048,
    )

    result = json.loads(response.choices[0].message.content)
    return result

@app.get("/")
async def root():
    return {"status": "ok"}