# PDF SCRAPING

Processing pdf document and extract all the abstract information.

Abstracts data is then processed into excel files where abstract details are linked for each author.

# Packages and Libraries

Python
Beautifulsoup
pandas

# Steps:

1. convert pdf to html using https://www.pdftohtml.net/
2. Html document is then processed with beautifulsoup to extract abstracts
3. The exctracted abstracts are then processed using python regex to identify authors, afflitations, abstact text, title etc., and the details are written into excel sheet for each author matched with corresponding afflitation.
