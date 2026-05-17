"use client";
import { useState } from "react";
import axios from "axios";

interface AnalysisResult {
  propositions: string[];
  verdict: string;
  reason: string;
  counterexample: string | null;
  logic_structure: {
    premises: string[];
    conclusion: string;
  };
}

interface DetailedResult {
  detailed_analysis: {
    proposition: string;
    converse: string;
    contrapositive: string;
    original_verdict: string;
    converse_verdict: string;
    contrapositive_verdict: string;
    explanation: string;
  }[];
  overall_conclusion: string;
}

export default function Home() {
  const [text, setText] = useState("");
  const [mode, setMode] = useState("argument");
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [detailedResult, setDetailedResult] = useState<DetailedResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);
  const [error, setError] = useState("");
  const [showDetail, setShowDetail] = useState(false);

  const analyze = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    setDetailedResult(null);
    setShowDetail(false);
    try {
      const res = await axios.post("https://gurapinganalyzer.onrender.com/analyze", {
        text,
        mode,
      });
      setResult(res.data);
    } catch (e) {
      setError("분석 중 오류가 발생했습니다. 백엔드 서버가 꺼져있다고 전해주세요.");
    }
    setLoading(false);
  };

  const analyzeDetail = async () => {
    if (!result) return;
    setDetailLoading(true);
    setShowDetail(true);
    try {
      const res = await axios.post("https://gurapinganalyzer.onrender.com/analyze-detail", {
        text,
        propositions: result.propositions,
      }, {
        headers: { "Content-Type": "application/json" }
      });
      setDetailedResult(res.data);
    } catch (e) {
      setError("상세 분석 중 오류가 발생했습니다. 다시 한번 시도해주세요.");
    }
    setDetailLoading(false);
  };

  const verdictColor =
    result?.verdict === "참"
      ? "text-green-600"
      : result?.verdict === "거짓"
      ? "text-red-600"
      : "text-yellow-600";

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-3xl mx-auto">

        <p className="text-xs text-gray-400 mb-2">창의인재부 동아리 봉사활동 프로젝트</p>

        <h1 className="text-3xl font-bold text-gray-800 mb-2">자료 분석기</h1>
        <p className="text-gray-500 mb-8">논증 또는 뉴스를 입력하면 명제를 추출하고 반례를 분석해드립니다.</p>

        <div className="flex gap-4 mb-4">
          <button
            onClick={() => setMode("argument")}
            className={`px-4 py-2 rounded-lg font-medium ${mode === "argument" ? "bg-blue-600 text-white" : "bg-white text-gray-600 border"}`}
          >
            논증 분석
          </button>
          <button
            onClick={() => setMode("news")}
            className={`px-4 py-2 rounded-lg font-medium ${mode === "news" ? "bg-blue-600 text-white" : "bg-white text-gray-600 border"}`}
          >
            뉴스/자료 분석
          </button>
        </div>

        <textarea
          className="w-full h-40 p-4 border rounded-lg text-gray-800 bg-white resize-none focus:outline-none focus:ring-2 focus:ring-blue-400"
          placeholder={mode === "argument" ? "예) 모든 인간은 죽는다. 소크라테스는 인간이다. 따라서 소크라테스는 죽는다." : "뉴스 기사나 아무 자료를 붙여넣으세요."}
          value={text}
          onChange={(e) => setText(e.target.value)}
        />

        <button
          onClick={analyze}
          disabled={loading}
          className="mt-4 w-full py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "분석 중..." : "분석 시작"}
        </button>

        {error && <p className="mt-4 text-red-500">{error}</p>}

        {result && (
          <div className="mt-8 space-y-4">
            <div className="bg-white rounded-lg p-6 border">
              <p className="text-sm text-gray-400 mb-1">판정</p>
              <p className={`text-2xl font-bold ${verdictColor}`}>{result.verdict}</p>
              <p className="text-gray-700 mt-2">{result.reason}</p>
            </div>

            {result.counterexample && (
              <div className="bg-red-50 rounded-lg p-6 border border-red-200">
                <p className="text-sm text-red-400 mb-1">반례</p>
                <p className="text-gray-800">{result.counterexample}</p>
              </div>
            )}

            <div className="bg-white rounded-lg p-6 border">
              <p className="text-sm text-gray-400 mb-3">논리 구조</p>
              <div className="space-y-2">
                {result.logic_structure.premises.map((p, i) => (
                  <div key={i} className="flex items-start gap-2">
                    <span className="text-blue-500 font-medium text-sm mt-0.5">전제 {i + 1}</span>
                    <p className="text-gray-700">{p}</p>
                  </div>
                ))}
                <div className="flex items-start gap-2 pt-2 border-t">
                  <span className="text-green-500 font-medium text-sm mt-0.5">결론</span>
                  <p className="text-gray-700">{result.logic_structure.conclusion}</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg p-6 border">
              <p className="text-sm text-gray-400 mb-3">추출된 명제</p>
              <ul className="space-y-1">
                {result.propositions.map((p, i) => (
                  <li key={i} className="text-gray-700">• {p}</li>
                ))}
              </ul>
            </div>

            <button
              onClick={analyzeDetail}
              disabled={detailLoading}
              className="w-full py-3 bg-gray-700 text-white rounded-lg font-semibold hover:bg-gray-800 disabled:opacity-50"
            >
              {detailLoading ? "상세 분석 중..." : "분석 상세 결과"}
            </button>

            {showDetail && detailedResult && (
              <div className="space-y-4">
                <h2 className="text-lg font-bold text-gray-800">상세 분석 결과</h2>

                {detailedResult.detailed_analysis.map((item, i) => (
                  <div key={i} className="bg-white rounded-lg p-6 border space-y-3">
                    <p className="font-semibold text-gray-800">명제 {i + 1}: {item.proposition}</p>
                    <div className="grid grid-cols-1 gap-2 text-sm">
                      <div className="bg-blue-50 rounded p-3">
                        <p className="text-blue-500 font-medium mb-1">역</p>
                        <p className="text-gray-700">{item.converse}</p>
                        <p className="mt-1 font-medium text-gray-600">판정: {item.converse_verdict}</p>
                      </div>
                      <div className="bg-purple-50 rounded p-3">
                        <p className="text-purple-500 font-medium mb-1">대우</p>
                        <p className="text-gray-700">{item.contrapositive}</p>
                        <p className="mt-1 font-medium text-gray-600">판정: {item.contrapositive_verdict}</p>
                      </div>
                      <div className="bg-gray-50 rounded p-3">
                        <p className="text-gray-500 font-medium mb-1">설명</p>
                        <p className="text-gray-700">{item.explanation}</p>
                      </div>
                    </div>
                  </div>
                ))}

                <div className="bg-gray-800 rounded-lg p-6 text-white">
                  <p className="text-sm text-gray-400 mb-1">종합 결론</p>
                  <p>{detailedResult.overall_conclusion}</p>
                </div>
              </div>
            )}
          </div>
        )}

        <div className="mt-12 pt-6 border-t">
          <p className="text-xs text-gray-400 text-center">
            ※ 참고: 상대적으로 최신 자료를 분석할 때는 오류 가능성 높음 주의(자료 부족 이슈)
            버그 제보-harryn7768@gmail.com
          </p>
        </div>

      </div>
    </main>
  );
}