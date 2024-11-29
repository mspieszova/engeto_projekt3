from bs4 import BeautifulSoup as bs
from requests import get
from urllib.parse import urlparse, parse_qs
import csv
import click




def najdi_tabulku(url):
    """
    Stáhne a zpracuje HTML obsah zadané webové stránky.

    Funkce provede HTTP GET požadavek na zadanou URL adresu. Pokud server vrátí 
    odpověď s kódem 200, zpracuje HTML obsah pomocí knihovny BeautifulSoup 
    a vrátí ho. V případě chyby status kódu nebo jiné výjimky vypíše chybovou 
    zprávu pomocí knihovny Click a vrátí None.

    :param url: URL adresa webové stránky, kterou chcete stáhnout a zpracovat.
    :type url: str
    :return: Vrací objekt BeautifulSoup obsahující zpracovaný HTML obsah, nebo None v případě chyby.
    :rtype: bs4.BeautifulSoup | None
    
    :raises Exception: Při neočekávané chybě během stahování URL.

    :Example:
    >>> html_parser = najdi_tabulku("https://example.com")
    >>> if html_parser:
    ...     print("HTML obsah úspěšně zpracován.")
    ... else:
    ...     print("Nepodařilo se zpracovat obsah webové stránky.")
    """
    try:
        # Odeslání požadavku na URL
        odpoved = get(url)
        
        # Kontrola status kódu odpovědi
        if odpoved.status_code == 200:
            return bs(odpoved.text, features="html.parser")
        else:
            click.echo("Chyba status kódu při navázání spojení se serverem webové stránky.")
            return None
    except Exception as e:
        # Ošetření neočekávané chyby
        click.echo(f"Chyba při stahování URL: {url}, chyba: {e}")
        return None


        

def vysbirej_url_adresy(rozdelene_html: str) -> list[str]:
    """
    Extrahuje všechny relevantní URL adresy z HTML obsahu a vrátí je jako seznam.

    Funkce prohledává zadaný HTML obsah a extrahuje URL adresy z tabulkových buněk
    odpovídajících zadaným kritériím. Pokud jsou nalezeny odkazy s konkrétními
    vlastnostmi, vyhledá také podstránky a jejich odkazy. Všechny adresy jsou vráceny 
    jako kompletní URL.

    :param rozdelene_html: HTML obsah stránky, který se má analyzovat.
    :type rozdelene_html: str
    :return: Seznam URL adres extrahovaných z tabulek HTML obsahu.
    :rtype: list[str]
    
    :Example:
    >>> html_parser = najdi_tabulku("https://www.volby.cz/pls/ps2017nss/vysledky")
    >>> url_list = vysbirej_url_adresy(html_parser)
    >>> print(url_list)
    ['https://www.volby.cz/pls/ps2017nss/url1', 'https://www.volby.cz/pls/ps2017nss/url2', ...]

    """
    vsechny_adresy = []
    for i in range(4):
        adr = rozdelene_html.find_all("td", {"headers": f"t{i}sa2"})
        if adr:
            for adresa in adr:
                adresa_z = adresa.find_all("a")
                for odkaz in adresa_z:
                    adresa_f = odkaz.get("href")
                    if int(adresa_f[3:4]) == 3:
                        adresa_spojena = f"https://www.volby.cz/pls/ps2017nss/{adresa_f}"
                        rozdelene_html_2 = najdi_tabulku(adresa_spojena)
                        if rozdelene_html_2:
                            adr_2 = rozdelene_html_2.find_all("td", {"headers": "s1"})
                            for adresa in adr_2:
                                adresa_z = adresa.find_all("a")
                                for odkaz in adresa_z:
                                    adresa_f = odkaz.get("href")
                                    adresa_spojena = f"https://www.volby.cz/pls/ps2017nss/{adresa_f}"
                                    vsechny_adresy.append(adresa_spojena)
                    else:
                        adresa_spojena = f"https://www.volby.cz/pls/ps2017nss/{adresa_f}"
                        vsechny_adresy.append(adresa_spojena)
    return vsechny_adresy





def ziskat_kod_obce(url):
    """
    Extrahuje hodnotu parametru "xobec" z URL adresy.

    Funkce zpracuje zadanou URL adresu, rozdělí její parametry a vrátí hodnotu 
    parametru "xobec". Pokud parametr "xobec" v URL neexistuje, vrátí `None`.

    :param url: URL adresa, ze které se má extrahovat parametr "xobec".
    :type url: str
    :return: Hodnota parametru "xobec", pokud existuje, jinak None.
    :rtype: str | None
    
    :raises ValueError: Pokud je zadaná URL adresa neplatná.

    :Example:
    >>> url = "https://example.com/page?xobec=12345&name=test"
    >>> ziskat_kod_obce(url)
    '12345'

    >>> url = "https://example.com/page?name=test"
    >>> ziskat_kod_obce(url)
    None
    """
    try:
        # Získání parametrů z URL
        query_params = parse_qs(urlparse(url).query)
        # Vrácení hodnoty parametru 'xobec', nebo None, pokud neexistuje
        return query_params.get("xobec", [None])[0]
    except Exception as e:
        raise ValueError(f"Chyba při zpracování URL: {url}, chyba: {e}")





def ziskej_data(rozdelene_html, url):
    """
    Extrahuje a zpracovává data z HTML obsahu a URL.

    Funkce extrahuje informace z HTML obsahu pomocí knihovny BeautifulSoup a doplní je o kód obce získaný z URL.
    Vrací strukturovaný slovník obsahující všechny nalezené hodnoty. V případě, že některé údaje chybí, vypíše 
    chybovou zprávu a vrátí částečně vyplněný slovník.

    :param rozdelene_html: Objekt BeautifulSoup obsahující zpracovaný HTML obsah stránky.
    :type rozdelene_html: bs4.BeautifulSoup
    :param url: URL adresa pro extrakci kódu obce.
    :type url: str
    :return: Slovník obsahující extrahované informace.
    :rtype: dict

    :raises AttributeError: Pokud některý z požadovaných prvků v HTML chybí.

    :Example:
    >>> from bs4 import BeautifulSoup
    >>> html_content = "<html>...</html>"  # HTML stránka jako string
    >>> soup = BeautifulSoup(html_content, "html.parser")
    >>> url = "https://example.com/page?xobec=12345"
    >>> ziskej_data(soup, url)
    {'code': '12345', 'location': 'Praha', 'Počet obyvatel': '1 200', ...}
    """
    # Inicializace slovníku s počáteční hodnotou 'code' z URL
    vysledky = {"code": ziskat_kod_obce(url)}
    
    # Vyhledání potřebných sekcí v HTML
    tabulka_1 = rozdelene_html.find("div", {"id": "publikace"})
    tabulka_2 = rozdelene_html.find("div", {"id": "publikace"})
    tabulka_3 = rozdelene_html.find_all("div", {"class": "t2_470"})
    
    try:
        # Získání lokace
        vysledky["location"] = (tabulka_2.find_all("h3"))[2].text.split(" ")[1]
        
        # Extrakce hodnot z tabulky 1
        vysledky[tabulka_1.find("th", {"id": "sa2"}).text.strip()] = tabulka_1.find("td", {"headers": "sa2"}).text.strip().replace('\xa0', '')
        vysledky[tabulka_1.find("th", {"id": "sa3"}).text.strip()] = tabulka_1.find("td", {"headers": "sa3"}).text.strip().replace('\xa0', '')
        vysledky[tabulka_1.find("th", {"id": "sa6"}).text.strip()] = tabulka_1.find("td", {"headers": "sa6"}).text.strip().replace('\xa0', '')
        
        # Zpracování tabulek třídy 't2_470'
        for tabulka_3_item in tabulka_3:
            for row in tabulka_3_item.find_all("tr"):
                columns = row.find_all("td")
                if len(columns) > 0:
                    name = columns[1].get_text(strip=True)
                    result = columns[2].get_text(strip=True).replace('\xa0', '')
                    vysledky[name] = result
    except AttributeError:
        click.echo("Některé údaje nebyly nalezeny.")
    
    # Vrácení výsledného slovníku
    return vysledky

def export_do_csv(vysledky_list, vystupni_soubor):
    """
    Exportuje seznam výsledků do CSV souboru.

    Funkce přijme seznam slovníků (každý obsahuje data pro jeden řádek), 
    a uloží je do CSV souboru se zadaným názvem souboru. Každý slovník v seznamu 
    musí mít stejné klíče, které budou použity jako názvy sloupců v CSV souboru.

    :param vysledky_list: Seznam slovníků obsahujících data, která mají být exportována.
    :type vysledky_list: list[dict]
    :param vystupni_soubor: Název CSV souboru, kam budou data exportována.
    :type vystupni_soubor: str
    :return: Funkce nevrací žádnou hodnotu. Výstup je uložen v CSV souboru.
    
    :Example:
    >>> vysledky = [{"name": "Kandidat A", "votes": 1000}, {"name": "Kandidat B", "votes": 900}]
    >>> export_do_csv(vysledky, "vysledky.csv")
    """
    with open(vystupni_soubor, "w", newline="", encoding="UTF-8") as f:
        fieldnames = vysledky_list[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(vysledky_list)




@click.command()
@click.argument("odkaz")
@click.argument("vystupni_soubor")

def cli(odkaz, vystupni_soubor):
    """
    Z webové stránky dané odkazem vyscarpuje volební výsledky a uloží je do CSV souboru.

    Funkce naváže spojení se serverem, stáhne HTML obsah hlavní stránky, extrahuje odkazy na podstránky,
    následně z těchto podstránek stáhne data a všechny výsledky uloží do CSV souboru.

    :param odkaz: URL adresa webové stránky, která obsahuje volební výsledky.
    :type odkaz: str
    :param vystupni_soubor: Název výstupního CSV souboru, kam se budou výsledky exportovat.
    :type vystupni_soubor: str
    :return: Funkce nevrací žádnou hodnotu. Výsledky jsou uloženy v CSV souboru.
    
    :Example:
    >>> cli("https://www.volby.cz/pls/ps2017nss/vysledky", "vysledky.csv")
    Navazuji spojení se serverem
    Parsuji data.
    Export hotov.
    """
    url_home = odkaz
    click.echo("Navazuji spojení se serverem")    
    prvotni_html = najdi_tabulku(url_home)
    click.echo("Parsuji data.")
    
    if prvotni_html:
        adresy = vysbirej_url_adresy(prvotni_html)
        vysledky_list = []

        for adresa in adresy:
            rozdelene_html = najdi_tabulku(adresa)
            if rozdelene_html:
                vysledky = ziskej_data(rozdelene_html, adresa)
                vysledky_list.append(vysledky)

        export_do_csv(vysledky_list, vystupni_soubor)
        click.echo("Export hotov.")



if __name__=="__main__":
    cli()


