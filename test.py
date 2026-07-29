from bs4 import BeautifulSoup
html=open('moteur.html', encoding='utf-8').read()
soup = BeautifulSoup(html, 'html.parser')
links = soup.find_all('a', href=lambda h: h and 'detail-annonce' in h)
for a in links[:2]:
    print("PARENT:", a.parent.name, a.parent.get('class'))
    print("A CLASS:", a.get('class'))
