import os
import sys
import logging
from dotenv import load_dotenv

# Ensure the root directory is in sys.path so we can import src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.presentation.api.dependencies import get_retrieval_service, get_document_agent

load_dotenv()
logging.basicConfig(level=logging.WARNING)

QA_PAIRS = [
    {
        "question": "Belgedeki ana kredi faiz oranı nedir?",
        "expected_keywords": ["faiz", "kredi", "oran", "%"]
    },
    {
        "question": "Sözleşmenin vade tarihi nedir?",
        "expected_keywords": ["vade", "tarih", "yıl", "ay"]
    },
    {
        "question": "Temerrüt durumunda uygulanacak cezai şartlar nelerdir?",
        "expected_keywords": ["temerrüt", "cezai", "şart", "gecikme", "ceza"]
    }
]

def calculate_overlap(answer: str, expected_keywords: list) -> float:
    answer_lower = answer.lower()
    match_count = sum(1 for kw in expected_keywords if kw.lower() in answer_lower)
    return match_count / len(expected_keywords)

def run_evaluation():
    print("====== Agentic Platform Değerlendirme Raporu ======\n")
    print("Agent başlatılıyor (Ollama ile)...\n")
    
    try:
        agent = get_document_agent()
        retrieval_service = get_retrieval_service()
        deps = {"retrieval_service": retrieval_service}
    except Exception as e:
        print(f"Hata: Servisler başlatılamadı. {e}")
        return

    total_score = 0
    passed_count = 0
    
    for i, qa in enumerate(QA_PAIRS, 1):
        question = qa["question"]
        expected = qa["expected_keywords"]
        
        print(f"[{i}/{len(QA_PAIRS)}] Soru: {question}")
        
        try:
            answer = agent.run(question, deps)
            
            # Print a snippet of the answer
            snippet = answer.replace("\n", " ")
            if len(snippet) > 80:
                snippet = snippet[:77] + "..."
            print(f"      Cevap Özeti: {snippet}")
            
            overlap_ratio = calculate_overlap(answer, expected)
            match_count = int(overlap_ratio * len(expected))
            passed = overlap_ratio >= 0.5
            
            status = "GEÇTİ" if passed else "KALDI"
            if passed:
                passed_count += 1
            total_score += overlap_ratio
            
            print(f"      Keyword Eşleşmesi: {match_count}/{len(expected)} ({overlap_ratio*100:.1f}%) -> {status}\n")
            
        except Exception as e:
            print(f"      Hata oluştu: {e}\n")

    avg_score = (total_score / len(QA_PAIRS)) * 100
    
    print("==================================================")
    print(f"Genel Başarı Durumu : {passed_count}/{len(QA_PAIRS)} Soru Geçildi")
    print(f"Ortalama Keyword Skoru: {avg_score:.1f}%")
    print("==================================================")

if __name__ == "__main__":
    run_evaluation()
