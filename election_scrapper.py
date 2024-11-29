from bs4 import BeautifulSoup as bs
from requests import get
from urllib.parse import urlparse, parse_qs
import csv
import click



def najdi_tabulku(url):
    try:
        odpoved = get(url)
        if odpoved.status_code == 200:           
            return bs(odpoved.text, features = "html.parser")
        else:
            click.echo("Chyba status codu při návázábí spojení se serverem webové stránky")
    except Exception as e:
        click.echo(f"Chyba při stahování URL: {url}, chyba: {e}")
        return None

        

def vysbirej_url_adresy(rozdelene_html:str):  
    vsechny_adresy = []
    for i in range(0,4):
        adr = rozdelene_html.find_all("td",{"headers":f"t{i}sa2"})
        if adr:
            for adresa in adr:
                adresa_z = adresa.find_all("a")
                for odkaz in adresa_z:                    
                    adresa_f = odkaz.get("href")
                    if int((adresa_f[3:4])) == 3:    
                        adresa_spojena = f"https://www.volby.cz/pls/ps2017nss/{adresa_f}"
                        rozdelene_html_2 = najdi_tabulku(adresa_spojena)
                        adr_2 = rozdelene_html_2.find_all("td",{"headers":"s1"})
                        for adresa in adr_2:
                            adresa_z = adresa.find_all("a")
                            for odkaz in adresa_z:                    
                                adresa_f=odkaz.get("href")
                                adresa_spojena = f"https://www.volby.cz/pls/ps2017nss/{adresa_f}"                                
                                vsechny_adresy.append(adresa_spojena)

                    else:
                        adresa_spojena = f"https://www.volby.cz/pls/ps2017nss/{adresa_f}"
                        vsechny_adresy.append(adresa_spojena)
                   
    return(vsechny_adresy)


def ziskat_kod_obce(url):
    query_params = parse_qs(urlparse(url).query)  # Rozdělí parametry v URL
    return query_params.get("xobec", [None])[0]  # Vrátí hodnotu parametru 'xobec'



def ziskej_data(rozdelene_html, url):
    vysledky = {"code": ziskat_kod_obce(url)}
    tabulka_1 = rozdelene_html.find("div", {"id": "publikace"})    
    tabulka_2 = rozdelene_html.find("div", {"id": "publikace"})  
    tabulka_3 = rozdelene_html.find_all("div", {"class": "t2_470"})     
    
    try:
        vysledky["location"]=(tabulka_2.find_all("h3"))[2].text.split(" ")[1]
        vysledky[tabulka_1.find("th", {"id": "sa2"}).text.strip()] = tabulka_1.find("td", {"headers": "sa2"}).text.strip().replace('\xa0', '')
        vysledky[tabulka_1.find("th", {"id": "sa3"}).text.strip()] = tabulka_1.find("td", {"headers": "sa3"}).text.strip().replace('\xa0', '')
        vysledky[tabulka_1.find("th", {"id": "sa6"}).text.strip()] = tabulka_1.find("td", {"headers": "sa6"}).text.strip().replace('\xa0', '')  
        for tabulka_3_item in tabulka_3:   
            for row in tabulka_3_item.find_all("tr"):
                columns = row.find_all("td")
                if len(columns) > 0:                 
                    name = columns[1].get_text(strip=True)
                    result = columns[2].get_text(strip=True).replace('\xa0', '')
                    vysledky[name] = result
    except AttributeError:
            click.echo("Některé údaje nebyly nalezeny.") 
  
    return(vysledky)    
  

def export_do_csv(vysledky_list, vystupní_soubor):
    with open(vystupní_soubor,"w",newline = "",encoding = "UTF-8") as f:
        fieldnames = vysledky_list[0].keys()
        writer = csv.DictWriter(f, fieldnames = fieldnames)
        writer.writeheader()
        writer.writerows(vysledky_list)




@click.command()
@click.argument("odkaz")
@click.argument("vystupni_soubor")

def cli(odkaz,vystupni_soubor):
    """
    z webové= stránky dané odkazem vyscarpuje volební výsledky a uloží je do csv souboru
    ODKAZ je webová adresa stránky
    VÝSTUPNI_SOUBOR je název výstupního souboru    
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

