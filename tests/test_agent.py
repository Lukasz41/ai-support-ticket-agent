from types import SimpleNamespace

import pytest
import agent


class ApiFailure(Exception):
    def __init__(self, code):
        self.code = code
        super().__init__(f"API error {code}")


class FakeModelClient:
    def __init__(self, outcomes):
        self.outcomes = iter(outcomes)
        self.calls = 0
        self.models = self

    def generate_content(self, **kwargs):
        self.calls += 1
        outcome = next(self.outcomes)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def test_retry_503_then_success():
    client = FakeModelClient([ApiFailure(503), SimpleNamespace(text='ok')])
    waits = []
    result = agent.generate_with_retry(
        client, model='test-model', contents='demo', config=None, sleep=waits.append
    )
    assert result.text == 'ok'
    assert client.calls == 2
    assert waits == [1]


def test_stops_after_three_503_failures():
    client = FakeModelClient([ApiFailure(503) for _ in range(3)])
    waits = []
    with pytest.raises(ApiFailure):
        agent.generate_with_retry(
            client, model='test-model', contents='demo', config=None, sleep=waits.append
        )
    assert client.calls == 3
    assert waits == [1, 2]


def test_does_not_retry_404():
    client = FakeModelClient([ApiFailure(404)])
    waits = []
    with pytest.raises(ApiFailure):
        agent.generate_with_retry(
            client, model='test-model', contents='demo', config=None, sleep=waits.append
        )
    assert client.calls == 1
    assert waits == []


def test_analyze_calls_tool_and_returns_structured_data(monkeypatch, tmp_path):
    import database
    monkeypatch.setenv('GEMINI_API_KEY', 'fake-for-test')
    monkeypatch.setattr(database, 'DB_PATH', tmp_path / 'tickets.db')
    database.init_db()
    database.save_ticket('WiFi broken after update', 'Network', 'Medium', 'Check driver')
    monkeypatch.setattr(agent, 'search_tickets', database.search_tickets)

    class FakeModels:
        def __init__(self):
            self.calls = 0

        def generate_content(self, *, model, contents, config):
            self.calls += 1
            if self.calls == 1:
                tool = config.tools[0]
                found = tool('wifi broken')
                assert len(found) == 1
                return SimpleNamespace(text='I found an older issue')
            return SimpleNamespace(text='{"category":"Network","priority":"Medium","solution":"Check driver"}')

    fake_models = FakeModels()
    monkeypatch.setattr(agent.genai, 'Client', lambda **kwargs: SimpleNamespace(models=fake_models))
    result = agent.analyze_ticket('My wifi is broken')
    assert result['tool_called'] is True
    assert len(result['matched_tickets']) == 1
    assert result['category'] == 'Network'
    assert fake_models.calls == 2
