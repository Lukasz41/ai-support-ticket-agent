import database


def test_save_and_read_ticket(tmp_path, monkeypatch):
    monkeypatch.setattr(database, 'DB_PATH', tmp_path / 'test.db')
    database.init_db()
    ticket_id = database.save_ticket('Printer offline', 'Hardware', 'Low', 'Check connection')
    rows = database.list_tickets()
    assert rows[0]['id'] == ticket_id
    assert rows[0]['description'] == 'Printer offline'


def test_search_finds_similar_wifi_ticket(tmp_path, monkeypatch):
    monkeypatch.setattr(database, 'DB_PATH', tmp_path / 'test.db')
    database.init_db()
    ticket_id = database.save_ticket(
        'Laptop cannot connect to Wi-Fi after Windows update',
        'Network', 'Medium', 'Check network drivers',
    )
    results = database.search_tickets('WiFi connection issue after update')
    assert results
    assert results[0]['id'] == ticket_id
    assert results[0]['solution'] == 'Check network drivers'


def test_search_with_no_matches(tmp_path, monkeypatch):
    monkeypatch.setattr(database, 'DB_PATH', tmp_path / 'test.db')
    database.init_db()
    database.save_ticket('Printer paper jam', 'Hardware', 'Low', 'Remove jam')
    assert database.search_tickets('wifi network problem') == []
