"""
Test suite for clinic agent nodes.
Place in project root (same level as the `graph` folder).
Run:  python test_agent.py   OR   pytest test_agent.py -v
"""

import sys
import os
import json
import types
import unittest
from unittest.mock import MagicMock, patch

# ── project root on sys.path so `graph` is the REAL package ──
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ═══════════════════════════════════════════════════════════════
# Stub all external libraries before any graph.* import happens.
# Order matters — stub parents before children.
# ═══════════════════════════════════════════════════════════════

def _stub(name: str) -> types.ModuleType:
    m = types.ModuleType(name)
    sys.modules[name] = m
    return m


def _make_clinic(name: str = "Test Clinic") -> MagicMock:
    clinic = MagicMock()
    clinic.name = name
    clinic.address = "123 Test St"
    clinic.info = "Test clinic info"
    clinic.doctors = []
    clinic.specialties = []
    clinic.services = []
    return clinic


def _setup_stubs() -> MagicMock:
    """Register all external-library stubs and return the shared fake_db."""

    # ── flask / flask_sqlalchemy / flask_login ──
    _stub("flask")
    _stub("flask_login")
    fsa = _stub("flask_sqlalchemy")

    class _FakeModel:
        query = MagicMock()

    fake_db = MagicMock()
    fake_db.Model = _FakeModel
    fsa.SQLAlchemy = MagicMock(return_value=fake_db)

    # ── sqlalchemy extras ──
    sa = _stub("sqlalchemy")
    sa.PrimaryKeyConstraint = MagicMock()
    sa.ForeignKeyConstraint = MagicMock()

    # ── dotenv / langchain ──
    _stub("dotenv").load_dotenv = MagicMock()
    _stub("langchain_google_genai").ChatGoogleGenerativeAI = MagicMock()

    # ── langchain_core messages ──
    lc_msgs = _stub("langchain_core.messages")
    _stub("langchain_core")

    class HumanMessage:
        def __init__(self, content):
            self.content = content

    class SystemMessage:
        def __init__(self, content):
            self.content = content

    lc_msgs.HumanMessage = HumanMessage
    lc_msgs.SystemMessage = SystemMessage

    # ── email_sender ──
    _stub("email_sender").EmailSender = MagicMock()

    # ── llm.model ──
    _stub("llm")
    _stub("llm.model").get_gemini = MagicMock()

    # ── models ──
    _stub("models")
    models_mod = _stub("models.models")
    models_mod.db = fake_db

    clinic_query = MagicMock()
    clinic_query.join.return_value.filter.return_value.first.return_value = _make_clinic()

    class _OrmBase:
        query = clinic_query

    def _orm_class(cls_name):
        """
        ORM stub whose constructor accepts keyword arguments and sets them
        as instance attributes — mirrors how SQLAlchemy models work and how
        nodes instantiate them: Booking(name=..., phone=..., ...).
        """
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
        return type(cls_name, (_OrmBase,), {"__init__": __init__})

    for cls_name in (
        "Clinic", "Page", "Doctor", "Specialty", "Service",
        "Platform", "Client", "User", "Booking", "Complaint",
    ):
        setattr(models_mod, cls_name, _orm_class(cls_name))

    models_mod.RequestCounter = MagicMock()

    # ── graph.prompt_service.clinic_data ──
    # Registered in sys.modules so that any `import` of the module gets
    # the fake.  _run() also patches the name inside each node's namespace
    # to handle `from graph.prompt_service.clinic_data import ClinicDataService`.
    _stub("graph.prompt_service")
    cd_mod = _stub("graph.prompt_service.clinic_data")

    class _FakeClinicDataService:
        @staticmethod
        def get_clinic_info(_):      return "Clinic: Test Clinic | 9am-9pm"
        @staticmethod
        def get_doctors_info(_):     return "Dr. Ali - Cardiology"
        @staticmethod
        def get_specialties_info(_): return "Cardiology"
        @staticmethod
        def get_services_info(_):    return "ECG - 200 EGP"

    cd_mod.ClinicDataService = _FakeClinicDataService

    return fake_db


# Run stubs once at module load time.
fake_db = _setup_stubs()


# ── Node module paths (used by patch()) ──
INTENT_MOD    = "graph.nodes.intent_node"
BOOKING_MOD   = "graph.nodes.booking_node"
COMPLAINT_MOD = "graph.nodes.complaint_node"
CLINIC_MOD    = "graph.nodes.clinic_Info_node"
DIRECT_MOD    = "graph.nodes.dirct_node"


# ═══════════════════════════════════════════════════════════════
# Shared test helpers
# ═══════════════════════════════════════════════════════════════

def fake_llm_response(content, input_tokens: int = 10, output_tokens: int = 20) -> MagicMock:
    """Return a mock LLM response; dict payloads are JSON-serialised automatically."""
    r = MagicMock()
    r.content = json.dumps(content) if isinstance(content, dict) else content
    r.usage_metadata = {"input_tokens": input_tokens, "output_tokens": output_tokens}
    return r


def make_model(payload) -> MagicMock:
    m = MagicMock()
    m.invoke.return_value = fake_llm_response(payload)
    return m


class NodeTestCase(unittest.TestCase):
    """
    Base class for node tests.

    Subclasses must declare:
        module_path  – dotted import path of the node module
        node_func    – name of the callable inside that module
        gemini_attr  – attribute name to patch for the LLM (default: "get_gemini")
    """

    module_path: str = ""
    node_func:   str = ""
    gemini_attr: str = "get_gemini"

    def _run(self, state: dict, payload) -> dict:
        from graph.prompt_service.clinic_data import ClinicDataService
        module = __import__(self.module_path, fromlist=[self.node_func])
        func   = getattr(module, self.node_func)
        # Two patches are needed:
        #   1. The LLM factory so we control the model response.
        #   2. ClinicDataService *inside the node module's namespace* because
        #      nodes use `from graph.prompt_service.clinic_data import …`,
        #      which binds the name locally — patching sys.modules alone
        #      won't override a name that's already been bound.
        with patch(f"{self.module_path}.{self.gemini_attr}", return_value=make_model(payload)):
            with patch(f"{self.module_path}.ClinicDataService", ClinicDataService, create=True):
                return func(state)

    def assertHasKeys(self, result: dict, *keys: str) -> None:
        for key in keys:
            self.assertIn(key, result, msg=f"Missing key: {key!r}")


# ═══════════════════════════════════════════════════════════════
# 1. Intent node
# ═══════════════════════════════════════════════════════════════

class TestIntentNode(NodeTestCase):
    module_path = INTENT_MOD
    node_func   = "intent_node"

    def _state(self, msg: str, summary: str = "", last_bot: str = "") -> dict:
        return {"user_message": msg, "summary": summary, "last_bot_message": last_bot}

    # ── happy paths ──
    def test_booking_intent(self):
        r = self._run(self._state("I want to book an appointment"), {"intent": "booking"})
        self.assertEqual(r["intent"], "booking")

    def test_clinic_info_intent(self):
        r = self._run(self._state("What are your working hours?"), {"intent": "clinic_info"})
        self.assertEqual(r["intent"], "clinic_info")

    def test_complaint_intent(self):
        r = self._run(self._state("I have a complaint"), {"intent": "complaint"})
        self.assertEqual(r["intent"], "complaint")

    def test_direct_intent_greeting(self):
        r = self._run(self._state("Hello!"), {"intent": "direct"})
        self.assertEqual(r["intent"], "direct")

    def test_arabic_booking_intent(self):
        r = self._run(self._state("عايز أحجز موعد"), {"intent": "booking"})
        self.assertEqual(r["intent"], "booking")

    def test_context_overrides_ambiguous_reply(self):
        r = self._run(
            self._state("Ahmed", last_bot="What is your full name for the booking?"),
            {"intent": "booking"},
        )
        self.assertEqual(r["intent"], "booking")

    # ── error / edge cases ──
    def test_malformed_json_falls_back_to_direct(self):
        r = self._run(self._state("???"), "NOT JSON AT ALL !!!")
        self.assertEqual(r["intent"], "direct")

    def test_markdown_wrapped_json_parsed(self):
        raw = '```json\n{"intent": "clinic_info"}\n```'
        r   = self._run(self._state("ما هي مواعيد العمل؟"), raw)
        self.assertEqual(r["intent"], "clinic_info")

    def test_empty_message_no_crash(self):
        r = self._run(self._state(""), {"intent": "direct"})
        self.assertIn(r["intent"], ["direct", "booking", "clinic_info", "complaint"])

    def test_usage_metadata_present(self):
        r = self._run(self._state("hi"), {"intent": "direct"})
        self.assertHasKeys(r, "intent_usage")
        self.assertHasKeys(r["intent_usage"], "input_tokens", "output_tokens")


# ═══════════════════════════════════════════════════════════════
# 2. Booking node
# ═══════════════════════════════════════════════════════════════

class TestBookingNode(NodeTestCase):
    module_path = BOOKING_MOD
    node_func   = "booking_node"

    _ALL_FIELDS = {
        "name": "Ahmed", "phone": "0501234567",
        "date": "2024-05-10", "details": "Dr. Ali",
    }

    def _state(self, msg: str = "", summary: str = "", lead_info: dict | None = None) -> dict:
        return {
            "page_id": "p1", "platform_id": "fb",
            "user_message": msg, "summary": summary,
            "last_bot_message": "", "lead_info": lead_info or {},
        }

    def _partial_payload(self, name, question):
        return {
            "lead_info": {"name": name, "phone": None, "date": None, "details": None},
            "next_question": question,
        }

    # ── happy paths ──
    def test_partial_name_asks_for_phone(self):
        r = self._run(
            self._state("My name is Ahmed"),
            self._partial_payload("Ahmed", "What is your phone number?"),
        )
        self.assertFalse(r["booking_saved"])
        self.assertEqual(r["response"],          "What is your phone number?")
        self.assertEqual(r["lead_info"]["name"], "Ahmed")

    def test_all_fields_saves_booking(self):
        fake_db.reset_mock()
        r = self._run(
            self._state("Dr. Ali please"),
            {"lead_info": self._ALL_FIELDS, "next_question": None},
        )
        self.assertTrue(r["booking_saved"])
        self.assertIn("Ahmed",      r["response"])
        self.assertIn("2024-05-10", r["response"])
        fake_db.session.add.assert_called_once()
        fake_db.session.commit.assert_called_once()

    def test_existing_fields_preserved_across_turns(self):
        payload = {
            "lead_info": {"name": "Sara", "phone": "0509999999", "date": None, "details": None},
            "next_question": "When would you like the appointment?",
        }
        r = self._run(
            self._state("0509999999", summary="name=Sara",
                        lead_info={"name": "Sara", "phone": None, "date": None, "details": None}),
            payload,
        )
        self.assertEqual(r["lead_info"]["name"],  "Sara")
        self.assertEqual(r["lead_info"]["phone"], "0509999999")

    def test_arabic_confirmation_contains_checkmark(self):
        payload = {
            "lead_info": {"name": "محمد", "phone": "0501111111",
                          "date": "2024-06-01", "details": "عيون"},
            "next_question": None,
        }
        r = self._run(self._state("تخصص عيون"), payload)
        self.assertIn("✅", r["response"])

    def test_summary_contains_extracted_name(self):
        r = self._run(
            self._state("Layla"),
            self._partial_payload("Layla", "Phone number?"),
        )
        self.assertIn("Layla", r["summary"])

    def test_comes_from_field_format(self):
        fake_db.reset_mock()
        saved = []
        fake_db.session.add.side_effect = lambda obj: saved.append(obj)
        self._run(self._state("done"), {"lead_info": self._ALL_FIELDS, "next_question": None})
        fake_db.session.add.side_effect = None
        self.assertTrue(saved, "booking_node never called db.session.add")
        self.assertEqual(saved[0].comes_from, "fb_p1")

    # ── error / edge cases ──
    def test_no_db_commit_when_fields_missing(self):
        fake_db.reset_mock()
        self._run(self._state("Omar"), self._partial_payload("Omar", "Phone?"))
        fake_db.session.commit.assert_not_called()

    def test_malformed_json_no_crash(self):
        r = self._run(self._state("hi"), "BROKEN {{{")
        self.assertIn("response", r)
        self.assertFalse(r["booking_saved"])

    def test_markdown_wrapped_booking_json(self):
        raw = f"```json\n{json.dumps({'lead_info': self._ALL_FIELDS, 'next_question': None})}\n```"
        r   = self._run(self._state("Dr. Ali"), raw)
        self.assertTrue(r["booking_saved"])


# ═══════════════════════════════════════════════════════════════
# 3. Complaint node
# ═══════════════════════════════════════════════════════════════

class TestComplaintNode(NodeTestCase):
    module_path = COMPLAINT_MOD
    node_func   = "complaint_node"

    def _state(self, msg: str = "", lead_info: dict | None = None, summary: str = "") -> dict:
        return {
            "page_id": "p1", "user_message": msg,
            "summary": summary, "last_bot_message": "",
            "lead_info": lead_info or {},
        }

    def _payload(self, phone, complaint, question=None):
        return {"lead_info": {"phone": phone, "complaint": complaint}, "next_question": question}

    # ── happy paths ──
    def test_partial_phone_asks_for_complaint(self):
        r = self._run(
            self._state("0501234567"),
            self._payload("0501234567", None, "Please describe your complaint."),
        )
        self.assertFalse(r["complaint_saved"])
        self.assertEqual(r["response"], "Please describe your complaint.")

    def test_all_fields_saves_complaint(self):
        fake_db.reset_mock()
        r = self._run(
            self._state("Doctor was rude"),
            self._payload("0501234567", "Doctor was rude"),
        )
        self.assertTrue(r["complaint_saved"])
        self.assertIn("✅", r["response"])
        fake_db.session.commit.assert_called_once()

    def test_phone_preserved_on_second_turn(self):
        r = self._run(
            self._state("Long wait", lead_info={"phone": "0501234567", "complaint": None}),
            self._payload("0501234567", "Long wait"),
        )
        self.assertEqual(r["lead_info"]["phone"], "0501234567")

    def test_arabic_complaint_saved(self):
        r = self._run(
            self._state("الطبيب لم يكن محترماً"),
            self._payload("0501111111", "الطبيب لم يكن محترماً"),
        )
        self.assertTrue(r["complaint_saved"])

    # ── error / edge cases ──
    def test_no_db_commit_when_complaint_missing(self):
        fake_db.reset_mock()
        self._run(
            self._state("0501234567"),
            self._payload("0501234567", None, "Describe your complaint."),
        )
        fake_db.session.commit.assert_not_called()

    def test_malformed_json_no_crash(self):
        r = self._run(self._state("hi"), "{{INVALID")
        self.assertIn("response", r)
        self.assertFalse(r["complaint_saved"])

    def test_usage_metadata_present(self):
        r = self._run(self._state("hi"), self._payload(None, None, "Phone?"))
        self.assertIn("complaint_usage", r)


# ═══════════════════════════════════════════════════════════════
# 4. Clinic info node
# ═══════════════════════════════════════════════════════════════

class TestClinicInfoNode(NodeTestCase):
    module_path = CLINIC_MOD
    node_func   = "clinic_info_node"

    def _state(self, msg: str = "What are your hours?", summary: str = "") -> dict:
        return {"page_id": "p1", "user_message": msg,
                "summary": summary, "last_bot_message": ""}

    # ── happy paths ──
    def test_returns_response_and_summary(self):
        r = self._run(self._state(), {"response": "We open 9am.", "summary": "Hours query."})
        self.assertEqual(r["response"], "We open 9am.")
        self.assertEqual(r["summary"],  "Hours query.")

    def test_last_bot_message_updated(self):
        r = self._run(self._state("Doctors?"), {"response": "Dr. Ali.", "summary": "Doctors."})
        self.assertEqual(r["last_bot_message"], "Dr. Ali.")

    def test_arabic_response_returned(self):
        r = self._run(
            self._state("ما هي مواعيد العمل؟"),
            {"response": "نفتح من 9 صباحاً.", "summary": "سأل عن المواعيد"},
        )
        self.assertIn("9", r["response"])

    # ── error / edge cases ──
    def test_malformed_json_regex_fallback(self):
        r = self._run(self._state(), '{"response": "We open at 9am", broken...')
        self.assertIn("9am", r["response"])

    def test_summary_kept_on_error(self):
        r = self._run(
            {"page_id": "p1", "user_message": "hi",
             "summary": "prev summary", "last_bot_message": ""},
            "TOTAL GARBAGE",
        )
        self.assertEqual(r["summary"], "prev summary")

    def test_usage_metadata_captured(self):
        r = self._run(self._state("hi"), {"response": "Hello.", "summary": "Greeting."})
        self.assertIn("clinic_info_usage", r)


# ═══════════════════════════════════════════════════════════════
# 5. Direct node
# ═══════════════════════════════════════════════════════════════

class TestDirectNode(NodeTestCase):
    module_path = DIRECT_MOD
    node_func   = "dirct_node"

    def _state(self, msg: str = "Hello!", summary: str = "") -> dict:
        return {"page_id": "p1", "user_message": msg,
                "summary": summary, "last_bot_message": ""}

    # ── happy paths ──
    def test_greeting_response(self):
        r = self._run(self._state(), {"response": "Hello! How can I help?", "summary": "Greeting."})
        self.assertEqual(r["response"], "Hello! How can I help?")

    def test_farewell(self):
        r = self._run(self._state("Bye!"), {"response": "Goodbye!", "summary": "Farewell."})
        self.assertIn("Goodbye", r["response"])

    def test_arabic_greeting(self):
        r = self._run(self._state("مرحبا"), {"response": "أهلاً! كيف أساعدك؟", "summary": "تحية."})
        self.assertIn("أهلاً", r["response"])

    def test_last_bot_message_updated(self):
        r = self._run(self._state(), {"response": "Hi there!", "summary": "Greeting."})
        self.assertEqual(r["last_bot_message"], "Hi there!")

    # ── error / edge cases ──
    def test_summary_preserved_on_json_error(self):
        r = self._run(
            {"page_id": "p1", "user_message": "hi",
             "summary": "previous summary", "last_bot_message": ""},
            "plain text no json",
        )
        self.assertEqual(r["summary"], "previous summary")

    def test_plain_text_fallback_is_string(self):
        r = self._run(self._state(), "Sorry, cannot help.")
        self.assertIsInstance(r["response"], str)

    def test_usage_metadata_present(self):
        r = self._run(self._state(), {"response": "Hi!", "summary": "Greeting."})
        self.assertIn("dirct_usage", r)


# ── runner ───────────────────────────────────────────────────────

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase
    all_tests = unittest.TestSuite([
        suite(TestIntentNode),
        suite(TestBookingNode),
        suite(TestComplaintNode),
        suite(TestClinicInfoNode),
        suite(TestDirectNode),
    ])
    result = unittest.TextTestRunner(verbosity=2).run(all_tests)
    sys.exit(0 if result.wasSuccessful() else 1)
