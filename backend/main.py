from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from groq import Groq
import os
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

class AnalysisRequest(BaseModel):
    text: str
    mode: str

class DetailRequest(BaseModel):
    text: str
    propositions: List[str]

SYSTEM_PROMPT = """
당신은 논리 분석 엔진입니다. 반드시 아래 JSON 형식으로만 응답하세요. 설명체 문장 금지. 또한 답변은 반드시 한글로만 이루어져 있어야합니다
반드시 아래 논리 규칙을 따르세요:
1. 명제가 참이면 대우도 반드시 참이어야 합니다.
2. 명제가 거짓이면 대우도 반드시 거짓이어야 합니다.
3. 역의 진리값은 명제와 달라도 됩니다.
4.또한 명제에 대한 반례가 없으면 'null'이 아닌 '판정이 참이므로 반례는 존재하지 않음'이라고 응답하세요. 
5. 종합 결론은 원래 명제, 역 명제, 대우 명제의 진리값과 논리적 관계를 고려하여 도출하세요.
6. 판별 근거 설명은 원래 명제, 역 명제, 대우 명제 각각의 진리값과 그 이유를 간결하게 설명하세요.
7.또한 명제를 도출할때, 명제는 사람에 따라 다르게 판단할 수 있는 주관적인 명제는 최대한 지양하고, 객관적으로 참/거짓이 판별 가능한 명제를 도출하세요
{
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
당신은 논리 분석 엔진입니다. 반드시 아래 JSON 형식으로만 응답하세요. 설명체 문장 금지.또한 답변은 반드시 한글로만 이루어져 있어야합니다
반드시 아래 논리 규칙을 따르세요:
1. 명제가 참이면 대우도 반드시 참이어야 합니다.
2. 명제가 거짓이면 대우도 반드시 거짓이어야 합니다.
3. 역의 진리값은 명제와 달라도 됩니다.
4.또한 명제에 대한 반례가 없으면 'null'이 아닌 '판정이 참이므로 반례는 존재하지 않음'이라고 응답하세요. 
5. 종합 결론은 원래 명제, 역 명제, 대우 명제의 진리값과 논리적 관계를 고려하여 도출하세요.
6. 판별 근거 설명은 원래 명제, 역 명제, 대우 명제 각각의 진리값과 그 이유를 간결하게 설명하세요.
7.또한 명제를 도출할때, 명제는 사람에 따라 다르게 판단할 수 있는 주관적인 명제는 최대한 지양하고, 객관적으로 참/거짓이 판별 가능한 명제를 도출하세요
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
        user_prompt = f"다음 텍스트에서 명제를 추출하고 각 명제의 참/거짓과 반례를 분석하세요. 또한 반례가 없을 경우에는 null이 아닌 '판정이 참이므로 반례는 존재하지 않음'이라고 응답하세요:\n\n{req.text}"
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
    props_text = "\n".join(req.propositions)
    user_prompt = f"원본 텍스트:\n{req.text}\n\n추출된 명제들:\n{props_text}"

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