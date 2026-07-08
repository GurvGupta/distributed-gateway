import re
from abc import ABC, abstractmethod
from models import ScanResult

class IScanningStrategy(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def scan(self, payload: str) -> ScanResult:
        pass

class SecretScanningStrategy(IScanningStrategy):
    @property
    def name(self) -> str:
        return "SecretDetector"

    def __init__(self):
        # Matches common patterns like AWS keys, generic bearer tokens, etc.
        self.patterns = [
            re.compile(r"(A3T[A-Z0-9]{14})"), # Simulated AWS Key
            re.compile(r"eyJhbGciOi")          # JWT header token start
        ]

    def scan(self, payload: str) -> ScanResult:
        findings = []
        for pattern in self.patterns:
            matches = pattern.findall(payload)
            if matches:
                findings.extend([f"Exposed Credential Token Match: {m[:8]}..." for m in matches])
        
        passed = len(findings) == 0
        return ScanResult(
            strategy_name=self.name,
            passed=passed,
            findings=findings,
            risk_score=1.0 if not passed else 0.0
        )

class PiiScanningStrategy(IScanningStrategy):
    @property
    def name(self) -> str:
        return "PiiDetector"

    def __init__(self):
        # Matches simulated Global ID or Credit Card sequences
        self.credit_card_pattern = re.compile(r"\b(?:\d[ -]*?){13,16}\b")

    def scan(self, payload: str) -> ScanResult:
        findings = []
        matches = self.credit_card_pattern.findall(payload)
        if matches:
            findings.extend(["Potential Payment Card Data Detected"])
        
        passed = len(findings) == 0
        return ScanResult(
            strategy_name=self.name,
            passed=passed,
            findings=findings,
            risk_score=0.8 if not passed else 0.0
        )