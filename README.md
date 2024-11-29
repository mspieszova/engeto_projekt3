# engeto_projekt3
## Popis

Tento program slouží k automatickému stahování a extrahování volebních výsledků z veřejně dostupné webové stránky (např. https://www.volby.cz) a následnému exportu těchto výsledků do CSV souboru. Program využívá knihovny `BeautifulSoup` pro parsování HTML a `requests` pro odesílání HTTP požadavků.

### Funkce programu:
1. **Stáhne HTML obsah stránky** - Na základě zadané URL adresy stáhne HTML obsah a provede jeho zpracování.
2. **Extrahuje URL adresy** - Získá odkazy na podstránky, které obsahují podrobné volební výsledky.
3. **Získá volební výsledky** - Z podstránek extrahuje specifické informace o volebních výsledcích, jako je počet hlasů pro jednotlivé kandidáty.
4. **Export do CSV** - Získané výsledky uloží do CSV souboru pro další analýzu.

## Instalace

Pro správnou funkčnost programu musíte mít nainstalovány následující knihovny:
- `beautifulsoup4`
- `requests`
- `click`
Knihovny, ketré jsou použity v kódu jsou uloženy v souboru requirements.txt. Při insatlaci doporučuji použít nové virtuální prostředí.
Pro instalaci těchto knihoven použijte pip:
pip install beautifulsoup4 requests click
nebo
pip install -r requirements.txt

## Použití

1. Stáhněte tento soubor na svůj počítač.
2. V příkazové řádce spusťte skript s těmito argumenty:
    - `odkaz`: URL adresu stránky obsahující volební výsledky.
    - `vystupni_soubor`: Cesta a název CSV souboru, kam chcete výsledky uložit.
python election_scrapper.py <odkaz-územního_celku> <vysledny-soubor>

### Příklad použití:
Pokud chcete stáhnout výsledky z webu https://www.volby.cz/pls/ps2017nss/vysledky a uložit je do souboru `vysledky.csv`, spusťte následující příkaz:
python script.py "https://www.volby.cz/pls/ps2017nss/vysledky" vysledky.csv

Po spuštění programu se:
- Naváže spojení se serverem.
- Stáhne HTML obsah hlavní stránky.
- Extrahují odkazy na podstránky s výsledky.
- Z těchto podstránek se získají volební výsledky a uloží do souboru `vysledky.csv`.

### Struktura výstupního CSV:
Výstupní CSV soubor bude obsahovat sloupce, které odpovídají získaným datům z webové stránky, například:
- `code` (kód obce)
- `location` (název obce)
- `Počet obyvatel` (počet obyvatel v obci)
- A další informace podle struktury tabulky na webu.

### Ukázka výstupního CSV:
code,location,Voličiv seznamu,Vydanéobálky,Platnéhlasy,...
565423,"Bdín",51,34,34,1,0,0,7,0,1,1,1,0,0,0,0,3,0,0,1,15,0,0,0,0,0,0,0,4,0
541672,"Branov",170,120,119,10,1,0,14,0,0,23,0,1,1,0,0,13,0,0,2,40,0,0,5,0,1,0,0,7,1
565041,"Břežany",106,71,69,6,0,0,4,1,4,12,0,1,1,0,0,9,0,0,2,20,0,0,0,0,0,2,0,6,1
...

## Licenční podmínky

Tento program je poskytován zdarma. Použití je na vlastní odpovědnost.

## Autor

Tento program vytvořil [Martina Spieszová].
