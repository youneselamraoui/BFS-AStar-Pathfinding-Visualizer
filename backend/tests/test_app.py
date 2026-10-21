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


def test_index_contains_comparison_ui():
    client = app.app.test_client()
    resp = client.get('/')
    html = resp.get_data(as_text=True)
    assert 'Tableau comparatif des performances' in html
    assert 'id="chart-nodes"' in html
    assert 'id="chart-time"' in html
    assert 'Benchmark rapide' in html
    assert 'Exporter en CSV' in html
    assert 'Effacer' in html
    assert 'https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js' in html


def test_index_manhattan_option_selected():
    client = app.app.test_client()
    resp = client.get('/')
    html = resp.get_data(as_text=True)
    assert '<option value="manhattan" selected>' in html
