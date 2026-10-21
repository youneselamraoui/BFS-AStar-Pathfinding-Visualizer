"""Tests Flask pour app.py"""
import app

def test_index_route_returns_200():
    client = app.app.test_client()
    resp = client.get('/')
    assert resp.status_code == 200

def test_index_contains_three_grids():
    client = app.app.test_client()
    resp = client.get('/')
    html = resp.get_data(as_text=True)
    assert '20x20' in html
    assert '50x50' in html
    assert '100x100' in html
