"""
FedAvg (Federated Averaging) implementation.
Coordinates local training across multiple nodes and aggregates model weights.
"""
import numpy as np
from typing import Dict, List, Tuple, Optional
from .model import LogisticRegression


def local_train(model: LogisticRegression, X: np.ndarray, y: np.ndarray,
                local_epochs: int = 3) -> Tuple[dict, float, int]:
    """
    Simulate local training at one node.

    Args:
        model: LogisticRegression model (will be modified in-place)
        X: local training features
        y: local training labels
        local_epochs: number of local SGD epochs

    Returns:
        weights: updated model weights
        avg_loss: average loss over local epochs
        n_samples: number of local samples
    """
    total_loss = 0.0
    for _ in range(local_epochs):
        loss = model.train_epoch(X, y)
        total_loss += loss
    avg_loss = total_loss / local_epochs
    return model.get_weights(), avg_loss, len(y)


def federated_average(weight_list: List[Tuple[dict, int]]) -> dict:
    """
    Aggregate weights from multiple nodes using FedAvg (weighted average by sample count).

    Args:
        weight_list: list of (weights_dict, n_samples) from each node

    Returns:
        Aggregated weights dict
    """
    total_samples = sum(n for _, n in weight_list)
    if total_samples == 0:
        return weight_list[0][0]

    # Weighted average
    avg_weights = np.zeros_like(weight_list[0][0]["weights"])
    avg_bias = 0.0
    for params, n in weight_list:
        fraction = n / total_samples
        avg_weights += fraction * params["weights"]
        avg_bias += fraction * params["bias"]

    return {"weights": avg_weights, "bias": avg_bias}


def run_fedavg(node_data: Dict[str, Tuple[np.ndarray, np.ndarray]],
               test_X: np.ndarray, test_y: np.ndarray,
               n_features: int,
               n_rounds: int = 5,
               local_epochs: int = 3,
               lr: float = 0.1,
               verbose: bool = True,
               print_fn=None) -> Dict:
    """
    Run the full FedAvg training loop.

    Args:
        node_data: {"node_name": (X_train, y_train)} for each participating node
        test_X: global test features
        test_y: global test labels
        n_features: number of input features
        n_rounds: number of federation rounds
        local_epochs: SGD epochs per node per round
        lr: learning rate
        verbose: whether to print progress
        print_fn: custom print function (e.g. for demo formatting)

    Returns:
        Dictionary with training history
    """
    out = print_fn or print

    # Initialize global model
    global_model = LogisticRegression(n_features, lr=lr)
    history = {"rounds": [], "test_acc": [], "node_losses": {}}
    for name in node_data:
        history["node_losses"][name] = []

    if verbose:
        out(f"  FedAvg: {len(node_data)} nodes, {n_rounds} rounds, "
            f"{local_epochs} local epochs, lr={lr}")
        out(f"  Features: {n_features}, Test samples: {len(test_y)}")
        for name, (X, y) in node_data.items():
            out(f"    {name}: {len(y)} samples (label distribution: "
                f"legal={int(np.sum(y==0))}, news={int(np.sum(y==1))})")
        out("")

    for rnd in range(1, n_rounds + 1):
        global_weights = global_model.get_weights()
        round_updates = []

        # Local training at each node
        for name, (X_local, y_local) in node_data.items():
            # Create local model with global weights
            local_model = LogisticRegression(n_features, lr=lr)
            local_model.set_weights(global_weights)

            # Train locally
            updated_weights, loss, n_samples = local_train(
                local_model, X_local, y_local, local_epochs
            )
            round_updates.append((updated_weights, n_samples))
            history["node_losses"][name].append(loss)

        # Aggregate
        aggregated = federated_average(round_updates)
        global_model.set_weights(aggregated)

        # Evaluate on test set
        acc = global_model.accuracy(test_X, test_y)
        history["rounds"].append(rnd)
        history["test_acc"].append(acc)

        if verbose:
            losses_str = ", ".join(
                f"{name}={history['node_losses'][name][-1]:.4f}"
                for name in node_data
            )
            out(f"  Round {rnd}/{n_rounds}: test_accuracy={acc:.4f}  "
                f"node_losses=[{losses_str}]")

    history["final_accuracy"] = history["test_acc"][-1] if history["test_acc"] else 0.0
    history["final_weights"] = global_model.get_weights()
    return history
