from dataclasses import dataclass
from typing import Optional
import random

from qiskit import QuantumCircuit


@dataclass
class BB84Result:
    n_qubits: int

    alice_bits: list[int]
    alice_bases: list[str]

    eve_enabled: bool
    intercept_rate: float
    intercepted: list[bool]
    eve_bases: list[Optional[str]]
    eve_bits: list[Optional[int]]

    bob_bases: list[str]
    bob_bits: list[int]

    sifted_indices: list[int]
    sifted_alice: list[int]
    sifted_bob: list[int]

    qber: float
    matching_bits: int
    mismatched_bits: int

    engine: str = "Qiskit BB84 probability simulation"


# ============================================================
# QISKIT REPRESENTATIVE CIRCUIT
# ============================================================

def build_preview_circuit(
    bit: int,
    alice_basis: str,
    bob_basis: str,
) -> QuantumCircuit:

    qc = QuantumCircuit(1, 1)

    # Alice prepares the BB84 state.
    if alice_basis == "Z":

        if bit == 1:
            qc.x(0)

    elif alice_basis == "X":

        qc.h(0)

        if bit == 1:
            qc.z(0)

    # Bob measures in his chosen basis.
    if bob_basis == "X":
        qc.h(0)

    qc.measure(0, 0)

    return qc


# ============================================================
# MAIN BB84 SIMULATION
# ============================================================

def run_bb84(
    n_qubits: int = 200,
    eve_enabled: bool = False,
    intercept_rate: float = 0.0,
    seed: Optional[int] = None,
) -> BB84Result:

    if not 20 <= n_qubits <= 300:
        raise ValueError(
            "Number of qubits must be between 20 and 300."
        )

    if not 0 <= intercept_rate <= 100:
        raise ValueError(
            "Interception rate must be between 0 and 100%."
        )

    rng = random.Random(seed)

    # --------------------------------------------------------
    # Alice
    # --------------------------------------------------------

    alice_bits = [
        rng.randint(0, 1)
        for _ in range(n_qubits)
    ]

    alice_bases = [
        rng.choice(["Z", "X"])
        for _ in range(n_qubits)
    ]

    # --------------------------------------------------------
    # Bob independently chooses bases
    # --------------------------------------------------------

    bob_bases = [
        rng.choice(["Z", "X"])
        for _ in range(n_qubits)
    ]

    # --------------------------------------------------------
    # Eve
    # --------------------------------------------------------

    intercepted = []
    eve_bases = []
    eve_bits = []

    bob_bits = []

    for i in range(n_qubits):

        # Default: Eve does nothing.
        is_intercepted = (
            eve_enabled
            and rng.random()
            < intercept_rate / 100.0
        )

        intercepted.append(is_intercepted)

        # ====================================================
        # NO EVE
        # ====================================================

        if not is_intercepted:

            eve_bases.append(None)
            eve_bits.append(None)

            if alice_bases[i] == bob_bases[i]:

                # Same basis gives the correct bit.
                bob_bit = alice_bits[i]

            else:

                # Different basis gives a random result.
                bob_bit = rng.randint(0, 1)

            bob_bits.append(bob_bit)

            continue

        # ====================================================
        # EVE INTERCEPT-RESEND
        # ====================================================

        eve_basis = rng.choice(
            ["Z", "X"]
        )

        eve_bases.append(eve_basis)

        # Eve measures Alice's state.
        if eve_basis == alice_bases[i]:

            eve_bit = alice_bits[i]

        else:

            # Wrong basis -> random measurement result.
            eve_bit = rng.randint(0, 1)

        eve_bits.append(eve_bit)

        # Eve prepares a new state using her result.
        # Bob now measures Eve's resent state.

        if bob_bases[i] == eve_basis:

            bob_bit = eve_bit

        else:

            # Different basis -> random result.
            bob_bit = rng.randint(0, 1)

        bob_bits.append(bob_bit)

    # ========================================================
    # SIFTING
    # ========================================================

    sifted_indices = [
        i
        for i in range(n_qubits)
        if alice_bases[i] == bob_bases[i]
    ]

    sifted_alice = [
        alice_bits[i]
        for i in sifted_indices
    ]

    sifted_bob = [
        bob_bits[i]
        for i in sifted_indices
    ]

    # ========================================================
    # QBER
    # ========================================================

    mismatched_bits = sum(
        alice_bit != bob_bit
        for alice_bit, bob_bit
        in zip(
            sifted_alice,
            sifted_bob,
        )
    )

    matching_bits = (
        len(sifted_alice)
        - mismatched_bits
    )

    if len(sifted_alice) > 0:

        qber = (
            mismatched_bits
            / len(sifted_alice)
            * 100
        )

    else:

        qber = 0.0

    return BB84Result(
        n_qubits=n_qubits,

        alice_bits=alice_bits,
        alice_bases=alice_bases,

        eve_enabled=eve_enabled,
        intercept_rate=(
            intercept_rate
            if eve_enabled
            else 0.0
        ),

        intercepted=intercepted,
        eve_bases=eve_bases,
        eve_bits=eve_bits,

        bob_bases=bob_bases,
        bob_bits=bob_bits,

        sifted_indices=sifted_indices,
        sifted_alice=sifted_alice,
        sifted_bob=sifted_bob,

        qber=qber,

        matching_bits=matching_bits,
        mismatched_bits=mismatched_bits,

        engine="Qiskit BB84 probability simulation",
    )


# ============================================================
# THEORETICAL REFERENCE
# ============================================================

def ideal_intercept_resend_qber(
    intercept_rate: float,
) -> float:

    # Full intercept-resend gives ~25% QBER
    # in the ideal asymptotic BB84 case.
    return 25.0 * intercept_rate / 100.0


# ============================================================
# SIMPLE SECURITY INTERPRETATION
# ============================================================

def assess_qber(
    qber: float,
    eve_enabled: bool,
) -> tuple[str, str]:

    if not eve_enabled:

        if qber < 5:

            return (
                "LOW DISTURBANCE",
                "Eve was OFF and the ideal channel produced very few errors.",
            )

        return (
            "ERRORS OBSERVED",
            "Eve was OFF, but this finite run produced noticeable errors.",
        )

    if qber < 5:

        return (
            "LOW DISTURBANCE OBSERVED",
            "This particular random run did not show strong disturbance.",
        )

    if qber < 15:

        return (
            "MEASURABLE DISTURBANCE",
            "The sifted key contains additional disagreements consistent with interference.",
        )

    return (
        "STRONG DISTURBANCE",
        "The elevated QBER is consistent with significant intercept-resend interference.",
    )