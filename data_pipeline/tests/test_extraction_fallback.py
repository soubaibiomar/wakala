import pytest
from bs4 import BeautifulSoup
from data_pipeline.kafka.producers.scrapers.extraction_fallback import FallbackExtractor

def test_extract_primary():
    html = '<div class="card"><span class="price">150 000 DH</span></div>'
    soup = BeautifulSoup(html, 'html.parser')
    
    price = FallbackExtractor.extract_text(
        soup, 
        primary_selector=".price", 
        fallbacks=[".fallback-price"]
    )
    assert price == "150 000 DH"

def test_extract_fallback():
    # Primary selector (.price) is missing, but fallback (.fallback-price) is there
    html = '<div class="card"><span class="fallback-price">120 000 DH</span></div>'
    soup = BeautifulSoup(html, 'html.parser')
    
    price = FallbackExtractor.extract_text(
        soup, 
        primary_selector=".price", 
        fallbacks=[".fallback-price", ".another-fallback"]
    )
    assert price == "120 000 DH"

def test_extract_heuristic():
    # Neither primary nor fallback selectors are present, but text has pattern
    html = '<div class="card"><p>A vendre belle voiture, 180000 MAD à débattre.</p></div>'
    soup = BeautifulSoup(html, 'html.parser')
    
    price = FallbackExtractor.extract_text(
        soup, 
        primary_selector=".price", 
        fallbacks=[".fallback-price"],
        heuristic="price"
    )
    # The heuristic should catch the "180000 MAD"
    assert "180000 MAD" in price

def test_extract_attr_fallback():
    html = '<div class="card"><a class="link2" href="/voiture/123">Details</a></div>'
    soup = BeautifulSoup(html, 'html.parser')
    
    href = FallbackExtractor.extract_attr(
        soup,
        primary_selector="a.link1",
        attr="href",
        fallbacks=["a.link2"]
    )
    assert href == "/voiture/123"
