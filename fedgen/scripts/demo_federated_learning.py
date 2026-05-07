#!/usr/bin/env python3
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fl.fl_demo import load_data_from_files, run_fl_demo
from scripts.fedgen_demo import banner, fail, info, ok, section


def load_live_data_from_k8s_backend():
    section("Step 1: Load live training data from FedGen backend")
    cmd = [
        "kubectl", "exec", "-n", "mvd", "deployment/fedgen-data-backend", "--",
        "python3", "-c",
        "import urllib.request,json; "
        "data={}; "
        "data['legal']=json.loads(urllib.request.urlopen('http://localhost:8080/legal/live', timeout=30).read()); "
        "data['news']=json.loads(urllib.request.urlopen('http://localhost:8080/news/live', timeout=30).read()); "
        "print(json.dumps(data))"
    ]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=60)
    data = json.loads(result.stdout)
    legal_data = data["legal"]
    news_data = data["news"]
    ok(f"Legal live data: {legal_data.get('metadata', {}).get('total_documents', 0)} documents")
    ok(f"News live data: {news_data.get('metadata', {}).get('total_articles', 0)} articles")
    info(f"Legal source: {legal_data.get('metadata', {}).get('source_api', 'OpenAlex')}")
    info(f"News source: {news_data.get('metadata', {}).get('source_api', 'Hacker News')}")
    return legal_data, news_data


def load_static_fallback():
    section("Step 1: Load local fallback training data")
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    legal_data, news_data = load_data_from_files(
        os.path.join(data_dir, "legal_sample.json"),
        os.path.join(data_dir, "news_sample.json"),
    )
    ok(f"Legal sample data: {len(legal_data.get('documents', []))} documents")
    ok(f"News sample data: {len(news_data.get('articles', []))} articles")
    return legal_data, news_data


def main():
    banner("Demo B: Federated Learning is Working", char="*")
    info("Purpose: prove the FedAvg federated learning loop trains a global text classifier.")
    info("Node A represents local legal data; Node B represents local news data.")
    info("Raw data stays local in the simulation; only model weights are aggregated.")

    try:
        legal_data, news_data = load_live_data_from_k8s_backend()
    except Exception as exc:
        info(f"Live backend unavailable, using static fallback: {exc}")
        legal_data, news_data = load_static_fallback()

    section("Step 2: Run FedAvg training")
    history = run_fl_demo(
        legal_data,
        news_data,
        n_rounds=5,
        local_epochs=3,
        max_features=300,
        lr=0.5,
        verbose=True,
        print_fn=lambda msg: print(f"  {msg}" if msg and not msg.startswith("  ") else msg),
    )

    banner("Demo B Result")
    if history.get("error"):
        fail(f"Federated learning demo failed: {history['error']}")
        return 1

    rounds = history.get("rounds", [])
    accuracies = history.get("test_acc", [])
    final_accuracy = history.get("final_accuracy", 0.0)
    ok(f"FedAvg completed {len(rounds)} federation rounds")
    ok(f"Final global model accuracy: {final_accuracy:.1%}")
    if len(accuracies) >= 2:
        info(f"Accuracy trace: {', '.join(f'{a:.1%}' for a in accuracies)}")
    ok("Local training losses were produced for each node")
    ok("Only model parameters were aggregated by the coordinator")
    return 0


if __name__ == "__main__":
    sys.exit(main())
