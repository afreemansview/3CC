import pytest

from chairs import disclosure, orchestrator, persona as personas, queue
from chairs.ledger import Ledger


class FakeProvider:
    def __init__(self, *replies):
        self.replies = list(replies)
        self.calls = []

    def generate(self, system, messages):
        self.calls.append((system, messages))
        return self.replies.pop(0)


@pytest.fixture
def ledger(tmp_path):
    return Ledger(tmp_path / "events.jsonl")


@pytest.fixture
def chair():
    return personas.load("the_other_chair")


@pytest.fixture
def convener():
    return personas.load("lucianof_dc")


def test_system_prompt_includes_persona_and_charter(chair, convener):
    prompt = personas.system_prompt(chair, convener, 200)
    assert "not a throne above humanity" in prompt
    assert "Red lines" in prompt
    assert "@Lucianof_DC" in prompt
    assert "200 characters" in prompt


def test_draft_adds_disclosure_and_logs(chair, convener, ledger):
    fake = FakeProvider("Point of order: who else is invited?")
    record = orchestrator.draft(chair, [(convener.x_handle, "Welcome.")], ledger,
                                counterpart=convener, provider=fake)
    assert record["text"].startswith("Point of order")
    assert "🤖 AI · OpenAI model · human-reviewed" in record["text"]
    assert queue.get(ledger, record["draft_id"])["status"] == "pending"
    _, messages = fake.calls[0]
    assert messages == [{"role": "user", "content": "@Lucianof_DC: Welcome."}]


def test_overlong_draft_gets_one_rewrite(chair, convener, ledger):
    fake = FakeProvider("x" * 400, "Shorter.")
    record = orchestrator.draft(chair, [(convener.x_handle, "Hi")], ledger, provider=fake)
    assert record["raw_output"] == "Shorter."
    assert len(fake.calls) == 2


def test_still_too_long_is_refused_not_truncated(chair, convener, ledger):
    fake = FakeProvider("x" * 400, "y" * 400)
    with pytest.raises(disclosure.TooLongError):
        orchestrator.draft(chair, [(convener.x_handle, "Hi")], ledger, provider=fake)
    assert ledger.events() == []


def test_own_posts_become_assistant_turns(chair, convener):
    messages = orchestrator.to_messages(chair, [
        (convener.x_handle, "a"), (chair.x_handle, "b"), ("@someone", "c"), (convener.x_handle, "d"),
    ])
    assert [m["role"] for m in messages] == ["user", "assistant", "user"]
    assert messages[-1]["content"] == "@someone: c\n\n@Lucianof_DC: d"


def test_queue_lifecycle(chair, ledger):
    ledger.append("drafted", "abc", persona=chair.id, text="t1")
    ledger.append("approved", "abc", text=disclosure.finalize(chair, "t2", edited=True), edited=True)
    d = queue.get(ledger, "abc")
    assert d["status"] == "approved" and d["edited"] and d["text"].endswith("✎")
    ledger.append("posted", "abc", post_id="123")
    assert queue.get(ledger, "abc")["status"] == "posted"
