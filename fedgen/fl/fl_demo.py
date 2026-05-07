"""
FedGen Federated Learning Demo
================================
Demonstrates FedAvg (Federated Averaging) using data acquired through EDC.

Can be run standalone or called from the main fedgen_demo.py.

Standalone usage:
    python -m fl.fl_demo                     # Use static sample data
    python -m fl.fl_demo --live              # Use live API data (requires data-backend)
    python -m fl.fl_demo --data legal.json news.json   # Use custom data files
"""
import json
import sys
import os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fl.data_utils import SimpleTfidfVectorizer, extract_texts_and_labels, split_by_node
from fl.fedavg import run_fedavg


def load_data_from_files(legal_path: str, news_path: str) -> tuple:
    """Load data from local JSON files."""
    with open(legal_path) as f:
        legal_data = json.load(f)
    with open(news_path) as f:
        news_data = json.load(f)
    return legal_data, news_data


def load_data_from_backend(legal_url: str, news_url: str) -> tuple:
    """Load data from the FedGen data backend (k8s-internal or port-forwarded)."""
    import urllib.request
    legal_data = json.loads(urllib.request.urlopen(legal_url, timeout=30).read())
    news_data = json.loads(urllib.request.urlopen(news_url, timeout=30).read())
    return legal_data, news_data


def run_fl_demo(legal_data: dict, news_data: dict,
                n_rounds: int = 5, local_epochs: int = 3,
                max_features: int = 300, lr: float = 0.5,
                verbose: bool = True, print_fn=None) -> dict:
    """
    Run the federated learning demonstration.

    Args:
        legal_data: JSON data from legal endpoint (has 'documents' key)
        news_data: JSON data from news endpoint (has 'articles' key)
        n_rounds: number of FedAvg rounds
        local_epochs: local SGD epochs per round per node
        max_features: TF-IDF vocabulary size
        lr: learning rate
        verbose: print progress
        print_fn: custom print function

    Returns:
        dict with training history and results
    """
    out = print_fn or print

    # Extract texts and labels
    texts, labels = extract_texts_and_labels(legal_data, news_data)
    n_legal = int(np.sum(labels == 0))
    n_news = int(np.sum(labels == 1))

    if verbose:
        out(f"  Dataset: {len(texts)} samples ({n_legal} legal + {n_news} news)")

    if len(texts) < 4:
        out("  ⚠ Too few samples for meaningful FL training. Need at least 4.")
        return {"error": "insufficient_data", "n_samples": len(texts)}

    # Split into node-local partitions (Non-IID)
    partitions, (test_texts, test_labels) = split_by_node(texts, labels)

    if verbose:
        out(f"  Node A (Legal Archives): {len(partitions['node_a'][1])} training samples")
        out(f"  Node B (News Syndicate): {len(partitions['node_b'][1])} training samples")
        out(f"  Shared test set: {len(test_labels)} samples")
        out("")

    # Vectorize all text
    all_train_texts = partitions["node_a"][0] + partitions["node_b"][0]
    vectorizer = SimpleTfidfVectorizer(max_features=max_features)
    vectorizer.fit(all_train_texts + test_texts)

    X_a = vectorizer.transform(partitions["node_a"][0])
    y_a = partitions["node_a"][1]
    X_b = vectorizer.transform(partitions["node_b"][0])
    y_b = partitions["node_b"][1]
    X_test = vectorizer.transform(test_texts)
    y_test = test_labels

    n_features = len(vectorizer.vocabulary_)
    if verbose:
        out(f"  TF-IDF features: {n_features}")
        out("")

    # Run FedAvg
    node_data = {
        "Node_A (Legal)": (X_a, y_a),
        "Node_B (News)": (X_b, y_b),
    }

    history = run_fedavg(
        node_data=node_data,
        test_X=X_test, test_y=y_test,
        n_features=n_features,
        n_rounds=n_rounds,
        local_epochs=local_epochs,
        lr=lr,
        verbose=verbose,
        print_fn=out,
    )

    # Summary
    if verbose:
        out("")
        final_acc = history["final_accuracy"]
        out(f"  Final global model accuracy: {final_acc:.1%}")
        if final_acc >= 0.7:
            out(f"  ✓ Federated model converged successfully!")
        else:
            out(f"  ℹ Model accuracy is low — likely due to small dataset size.")
        out(f"  ℹ Data never left local nodes — only model weights were shared.")

    return history


def main():
    """Standalone entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="FedGen FL Demo")
    parser.add_argument("--live", action="store_true",
                       help="Use live API data from data backend")
    parser.add_argument("--backend-url", default="http://localhost:8080",
                       help="Data backend base URL (for --live)")
    parser.add_argument("--data", nargs=2, metavar=("LEGAL", "NEWS"),
                       help="Paths to legal and news JSON files")
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--epochs", type=int, default=3)
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("  FedGen Federated Learning Demo (Standalone)")
    print("=" * 60 + "\n")

    if args.data:
        print(f"  Loading data from files: {args.data[0]}, {args.data[1]}")
        legal_data, news_data = load_data_from_files(args.data[0], args.data[1])
    elif args.live:
        print(f"  Loading live data from: {args.backend_url}")
        legal_data, news_data = load_data_from_backend(
            f"{args.backend_url}/legal/live",
            f"{args.backend_url}/news/live"
        )
    else:
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        print(f"  Loading static sample data from: {data_dir}")
        legal_data, news_data = load_data_from_files(
            os.path.join(data_dir, "legal_sample.json"),
            os.path.join(data_dir, "news_sample.json")
        )

    print()
    history = run_fl_demo(legal_data, news_data,
                          n_rounds=args.rounds, local_epochs=args.epochs)

    print("\n" + "=" * 60)
    if history.get("error"):
        print("  Demo completed with warnings.")
    else:
        print("  Demo completed successfully!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
