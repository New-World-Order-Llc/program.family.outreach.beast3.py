# program.family.outreach.beast3.py
# Beast System 3.0 — Deterministic Outreach & Engagement Module

from dataclasses import dataclass, field
import time
import hashlib

@dataclass
class OutreachEvent:
    event_type: str
    metadata: dict
    ts: float = field(default_factory=time.time)

@dataclass
class OutreachProfile:
    family_id: str
    contacts: list = field(default_factory=list)
    followups: list = field(default_factory=list)
    risk_flags: list = field(default_factory=list)
    last_update: float = field(default_factory=time.time)

    def log_contact(self, channel: str, note: str):
        entry = OutreachEvent(
            event_type="contact",
            metadata={"channel": channel, "note": note}
        )
        self.contacts.append(entry)
        self.last_update = entry.ts

    def schedule_followup(self, ts: float, reason: str):
        entry = {
            "ts": ts,
            "reason": reason,
            "created": time.time()
        }
        self.followups.append(entry)
        self.last_update = entry["created"]

    def flag_risk(self, category: str, severity: str):
        entry = OutreachEvent(
            event_type="risk_flag",
            metadata={"category": category, "severity": severity}
        )
        self.risk_flags.append(entry)
        self.last_update = entry.ts

class OutreachEngine:
    def __init__(self, kernel):
        self.kernel = kernel
        self.profiles = {}

    def create_profile(self, family_id: str):
        profile = OutreachProfile(family_id)
        self.profiles[family_id] = profile

        return self.kernel.dispatch(
            module="family.outreach",
            action="create_profile",
            payload={"family_id": family_id}
        )

    def contact_family(self, family_id: str, channel: str, note: str):
        if family_id not in self.profiles:
            raise ValueError("Outreach profile not found")

        profile = self.profiles[family_id]
        profile.log_contact(channel, note)

        return self.kernel.dispatch(
            module="family.outreach",
            action="contact_family",
            payload={"family_id": family_id, "channel": channel, "note": note}
        )

    def schedule_followup(self, family_id: str, ts: float, reason: str):
        if family_id not in self.profiles:
            raise ValueError("Outreach profile not found")

        profile = self.profiles[family_id]
        profile.schedule_followup(ts, reason)

        return self.kernel.dispatch(
            module="family.outreach",
            action="schedule_followup",
            payload={"family_id": family_id, "ts": ts, "reason": reason}
        )

    def flag_risk(self, family_id: str, category: str, severity: str):
        if family_id not in self.profiles:
            raise ValueError("Outreach profile not found")

        profile = self.profiles[family_id]
        profile.flag_risk(category, severity)

        return self.kernel.dispatch(
            module="family.outreach",
            action="flag_risk",
            payload={"family_id": family_id, "category": category, "severity": severity}
        )

    def get_profile(self, family_id: str):
        return self.profiles.get(family_id, None)
