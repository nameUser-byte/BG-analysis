import base64
import os

out_dir = "C:/Users/chan/.gemini/antigravity/brain/096d8107-72a1-4639-b057-0688c98b6723"
html_path = "c:/Users/chan/Documents/semiconductor-ai-project/index.html"

def image_to_base64(filepath):
    try:
        with open(filepath, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            return f"data:image/png;base64,{encoded_string}"
    except FileNotFoundError:
        return ""

img_corr = image_to_base64(f"{out_dir}/corr_matrix.png")
img_tool = image_to_base64(f"{out_dir}/tool_matching.png")
img_drift = image_to_base64(f"{out_dir}/chamber_age_drift.png")
img_rf = image_to_base64(f"{out_dir}/rf_selectivity.png")
img_epd = image_to_base64(f"{out_dir}/epd_overetch.png")

html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dry Etch 공정 분석 리포트</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f3f4f6; }}
        .card {{ background: white; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); padding: 20px; margin-bottom: 20px; }}
        .header {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 30px; }}
    </style>
</head>
<body class="p-8">

    <div class="max-w-6xl mx-auto">
        <div class="header shadow-lg">
            <h1 class="text-3xl font-bold">반도체 Dry Etch 공정 AI 분석 리포트</h1>
            <p class="text-lg mt-2">데이터 클렌징, 탐색적 데이터 분석(EDA) 및 공선성 검증 결과</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            <div class="card">
                <h2 class="text-xl font-semibold mb-4 text-blue-800 border-b pb-2">1. 데이터 전처리 결과</h2>
                <ul class="list-disc pl-5 text-gray-700 space-y-2">
                    <li><strong>원본 데이터:</strong> 805행</li>
                    <li><strong>중복 제거:</strong> 완전히 동일한 5행 삭제</li>
                    <li><strong>단위 보정:</strong> 온도(K &rarr; &deg;C 변환), 유량/압력 스케일 보정</li>
                    <li><strong>오류 정제:</strong> 식각 선택비 음수(-1.14) 등 물리적 오류 데이터 삭제</li>
                    <li><strong>결측치 처리:</strong> 통신 오류로 인한 극한값 NaN 처리 후 설비(Tool)별 중앙값 대체</li>
                    <li><strong>최종 확보 데이터:</strong> 799행 (결측치 0%)</li>
                </ul>
            </div>

            <div class="card">
                <h2 class="text-xl font-semibold mb-4 text-blue-800 border-b pb-2">2. 다중공선성(VIF) 검증</h2>
                <p class="text-gray-700 mb-2">모든 독립 변수의 VIF 지수가 기준치(10)를 크게 하회하여 공선성 문제가 없습니다.</p>
                <div class="overflow-x-auto">
                    <table class="min-w-full bg-white border">
                        <thead class="bg-gray-100">
                            <tr>
                                <th class="py-2 px-4 border-b text-left">Feature</th>
                                <th class="py-2 px-4 border-b text-left">VIF</th>
                            </tr>
                        </thead>
                        <tbody class="text-sm">
                            <tr><td class="py-1 px-4 border-b">endpoint_time_s</td><td class="py-1 px-4 border-b">1.63</td></tr>
                            <tr><td class="py-1 px-4 border-b">chamber_age_runs</td><td class="py-1 px-4 border-b">1.35</td></tr>
                            <tr><td class="py-1 px-4 border-b">rf_source_w</td><td class="py-1 px-4 border-b">1.27</td></tr>
                            <tr><td class="py-1 px-4 border-b">Others</td><td class="py-1 px-4 border-b">&lt; 1.05</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>

        </div>

        <div class="card mt-6">
            <h2 class="text-2xl font-semibold mb-6 text-blue-800 border-b pb-2">3. 핵심 EDA 시각화 결과</h2>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
                <div>
                    <h3 class="font-bold text-lg text-gray-800 mb-2">A. 상관계수 매트릭스</h3>
                    <p class="text-sm text-gray-600 mb-3">각 공정 파라미터와 품질 지표 간의 상관관계를 보여줍니다.</p>
                    <img src="{img_corr}" alt="Correlation Matrix" class="w-full border rounded">
                </div>
                <div>
                    <h3 class="font-bold text-lg text-gray-800 mb-2">B. 설비 간 편차 (Tool-to-Tool)</h3>
                    <p class="text-sm text-gray-600 mb-3">T04 설비가 타 설비 대비 CD Bias와 선택비가 낮은 경향이 있습니다.</p>
                    <img src="{img_tool}" alt="Tool Matching" class="w-full border rounded">
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                    <h3 class="font-bold text-md text-gray-800 mb-2">C. 챔버 노후도에 따른 Drift</h3>
                    <p class="text-xs text-gray-600 mb-2">PM 이후 챔버 사용 횟수 증가 시 CD Bias가 점진적으로 양(+) 방향 이동함이 모든 설비에서 관측되었습니다.</p>
                    <img src="{img_drift}" alt="Chamber Age Drift" class="w-full border rounded">
                </div>
                <div>
                    <h3 class="font-bold text-md text-gray-800 mb-2">D. 물리적 특성: RF Bias vs Selectivity</h3>
                    <p class="text-xs text-gray-600 mb-2">RF Bias Power(이온 충돌 에너지)가 강할수록 식각 선택비가 떨어지는 현상을 입증합니다 (r=-0.92).</p>
                    <img src="{img_rf}" alt="RF Bias vs Selectivity" class="w-full border rounded">
                </div>
                <div>
                    <h3 class="font-bold text-md text-gray-800 mb-2">E. 센서 불량 예측: EPD vs Overetch</h3>
                    <p class="text-xs text-gray-600 mb-2">식각 종료 신호(EPD Slope) 및 소요 시간을 통해 과식각 위험도를 군집화할 수 있습니다.</p>
                    <img src="{img_epd}" alt="EPD vs Overetch Risk" class="w-full border rounded">
                </div>
            </div>
        </div>

    </div>

</body>
</html>
"""

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"index.html successfully created at: {html_path}")
