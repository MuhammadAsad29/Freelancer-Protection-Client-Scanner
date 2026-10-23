import math
import sys

import laya
from laya.confidence import answer_confidence_value

# Windows consoles default to cp1252, which cannot render symbols like "✓".
# Force UTF-8 output so status messages never crash the process.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


class LayaEngine:
    """Turns a freelance job post into a risk verdict using the LAYA decision model.

    LAYA answers typed questions in one forward pass. Each question comes back
    as an answer dict inside the result's "answers" map, keyed by question id:

        choice -> {"choice": <label>, "probabilities": {...}, "answer_confidence": <float>}
        noul   -> {"noul": <P(true)>, "answer_confidence": <float>}

    A question names the state field it reads in backticks, which is how LAYA
    knows which part of the state to look at.
    """

    STATE_FIELD = "job_description"

    # Each option carries a description: bare labels ("scam", "toxic") are too
    # thin for the model to match a job post against, while a concrete
    # description gives it something to match on.
    TRAP_CRITERIA = {
        "unrealistic_budget_sweatshop": (
            "A tiny fixed budget for an enormous amount of work, "
            "or an impossible deadline for the scope."
        ),
        "nightmare_micromanager": (
            "Demands round-the-clock availability, constant chat, daily standups, "
            "or micromanagement and interruptions."
        ),
        "unpaid_sample_demand": (
            "Asks for free sample work, a trial task, or a test project "
            "before hiring or paying the freelancer."
        ),
        "telegram_crypto_scam": (
            "Tries to move off-platform to Telegram, WhatsApp, crypto, "
            "or an upfront fee, or asks for an upfront payment."
        ),
        "legitimate_fair_client": (
            "A fair job with a reasonable budget, a clear scope, "
            "and normal on-platform communication."
        ),
    }

    # How dangerous each trap is on the 1..5 scale. The trap type is the
    # headline verdict, so this is what a recognised trap is worth on its own.
    TRAP_SEVERITY = {
        "unrealistic_budget_sweatshop": 4,
        "nightmare_micromanager": 4,
        "unpaid_sample_demand": 3,
        "telegram_crypto_scam": 5,
        "legitimate_fair_client": 1,
    }

    BANDS = ["safe", "slightly risky", "risky", "very risky", "scam-grade"]

    EXPLANATIONS = {
        "unrealistic_budget_sweatshop": (
            "Budget is dangerously low for the scope requested -- classic sweatshop pricing."
        ),
        "nightmare_micromanager": (
            "Client shows signs of demanding unrealistic availability or heavy micromanagement."
        ),
        "unpaid_sample_demand": (
            "Client is demanding free sample work or a test task before hiring you."
        ),
        "telegram_crypto_scam": (
            "Warning: the client appears to be moving off-platform (Telegram/crypto) "
            "to dodge Upwork protection."
        ),
        "legitimate_fair_client": (
            "Job looks clean: realistic expectations, clear scope, and fair pay."
        ),
    }

    def __init__(self, model_name: str = "convaiinnovations/laya"):
        print(f"[*] Loading official LAYA Decision Model ({model_name})...")
        self.agent = laya.load(model_name)
        print("[✓] LAYA Engine loaded successfully in RAM.")

    def _questions(self) -> dict:
        return {
            "is_toxic": {
                "type": "noul",
                "instructions": (
                    f"Does `{self.STATE_FIELD}` contain scam signals, exploit the freelancer, "
                    "or offer terms that are unfair for a freelancer?"
                ),
                "criteria": {
                    "false": "a normal job with fair, reasonable terms",
                    "true": "a job with exploitation, scam, or non-payment risk",
                },
            },
            "trap_type": {
                "type": "choice",
                "instructions": (
                    f"What is the primary risk or trap type in `{self.STATE_FIELD}`?"
                ),
                "criteria": dict(self.TRAP_CRITERIA),
            },
        }

    # -- answer readers -------------------------------------------------

    @staticmethod
    def _noul_probability(answer: dict) -> float:
        """P(true) for a noul answer."""
        try:
            return float(answer.get("noul", 0.0))
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _choice_label(answer: dict) -> str:
        label = answer.get("choice")
        if not isinstance(label, str) or not label:
            # A missing answer must not read as "some unknown trap" -- that would
            # flag a job as toxic when the model actually failed to answer.
            return "legitimate_fair_client"
        return label

    # -- analysis -------------------------------------------------------

    def analyze_full_job(self, job_text: str) -> dict:
        result = self.agent.predict(
            state={self.STATE_FIELD: job_text},
            questions=self._questions(),
        )
        answers = result.get("answers") or {}

        toxic_answer = answers.get("is_toxic") or {}
        trap_answer = answers.get("trap_type") or {}

        toxic_probability = self._noul_probability(toxic_answer)
        trap_type = self._choice_label(trap_answer)

        # The trap classification is the sharp signal, so it decides the verdict;
        # the noul probability can only add a flag, never clear one. A job that
        # reads as a known trap is toxic even when the noul head stays cautious.
        is_toxic = trap_type != "legitimate_fair_client" or toxic_probability >= 0.5

        # Danger score = the more severe of two independent readings:
        #   * the severity of the trap type the model recognised, and
        #   * the overall risk probability (P(toxic) scaled onto 1..5).
        # Both readings are continuous or well-separated, so neither can flip the
        # verdict the way a single near-tied score head does -- the noul acts as
        # a floor that keeps a recognised trap off the safe end, and the trap
        # type escalates a job the noul only mildly dislikes.
        trap_severity = self.TRAP_SEVERITY.get(trap_type, 1)
        risk_level = toxic_probability * 4 + 1
        # Half-up rounding: Python's round() is half-to-even, which would send a
        # 2.5 down to 2 and a 3.5 up to 4 on a danger scale.
        score = max(1, min(5, math.floor(max(trap_severity, risk_level) + 0.5)))

        confidence = answer_confidence_value(trap_answer)
        if confidence is None:
            confidence = 0.0

        reason = self.EXPLANATIONS.get(trap_type, "Proceed with normal diligence.")

        usage = result.get("usage") or {}
        truncated = bool(usage.get("truncated"))
        if truncated:
            reason += (
                " (The posting was too long to read in full, so some details may be missing.)"
            )

        return {
            "is_toxic": bool(is_toxic),
            "toxicity_score": score,
            "trap_type": trap_type,
            "confidence": round(float(confidence), 4),
            "reason": reason,
            "toxicity_probability": round(toxic_probability, 4),
            "danger_band": self.BANDS[score - 1],
            "truncated": truncated,
        }
