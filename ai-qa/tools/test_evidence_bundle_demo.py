import os
import sys
import json
import yaml

AI_QA_ROOT = r"d:\artemis\ai-qa"
sys.path.insert(0, AI_QA_ROOT)

from orchestrator.main import generate_hermes_evidence_bundle

def demo():
    tc_file = os.path.join(AI_QA_ROOT, "testcases", "ai-help-agent", "KONG-AI-001.yaml")
    with open(tc_file, "r", encoding="utf-8") as f:
        tc_data = yaml.safe_load(f)

    mock_steps = [
        {"step": 1, "desc": "Mở Drawer Menu", "action": "tap_selector", "duration_sec": 0.8, "status": "OK"},
        {"step": 2, "desc": "Chọn mục Kong AI", "action": "tap_selector", "duration_sec": 1.2, "status": "OK"},
        {"step": 3, "desc": "Chờ giao diện trợ lý ảo load", "action": "wait", "duration_sec": 1.5, "status": "OK"}
    ]
    
    mock_screenshot = os.path.join(AI_QA_ROOT, "runs", "KONG-AI-001_final.png")
    mock_texts = [
        "Kong AI Assistant", "How can I help you today?", 
        "Ask me to find customers, check jobs, or create estimates", 
        "Type a message...", "Send", "Microphone"
    ]
    mock_crash = {"has_crash": False, "crash_lines": []}
    
    ev_json, ev_prompt = generate_hermes_evidence_bundle(
        tc_data, mock_steps, 3.5, mock_screenshot, mock_texts, mock_crash, "LIKELY_PASS"
    )
    print("DEMO EVIDENCE GENERATED:")
    print("JSON:", ev_json)
    print("MARKDOWN:", ev_prompt)

if __name__ == "__main__":
    demo()
