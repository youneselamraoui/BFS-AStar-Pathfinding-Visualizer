"""Tests Flask pour app.py"""
import app

def test_index_route_returns_200():
    client = app.app.test_client()
    resp = client.get('/')
    assert resp.status_code == 200

def test_index_contains_dynamic_elements():
    client = app.app.test_client()
    resp = client.get('/')
    html = resp.get_data(as_text=True)
    # presence of two canvases
    assert html.count('<canvas') >= 2
    assert 'Comparer les deux' in html
    assert '<script src="/static/app.js"></script>' in html
