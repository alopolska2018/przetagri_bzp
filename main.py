import requests
import xml.etree.ElementTree as ET
import json
import pandas as pd
import streamlit as st
import base64
from io import BytesIO


def zp400_wg_kryteriow(cpv_glowny_przedmiot, rodzaj_zamawiajacego='99', rodzaj_zamowienia='1', tryb_udzielenia_zamowienia='99', czyGrupaCPV='1', calkowita_wart_zam_od='-1', calkowita_wart_zam_do='-1'):
    url = ' http://websrv.bzp.uzp.gov.pl/BZP_PublicWebService.asmx/ogloszeniaZP400KryteriaWyszukiwaniaJSON'
    headers = {'content-type': 'text/xml'}
    payload = {'_rodzaj_zamawiajacego': rodzaj_zamawiajacego, '_rodzaj_zamowienia': rodzaj_zamowienia, '_tryb_udzielenia_zamowienia': tryb_udzielenia_zamowienia, '_czyGrupaCPV': czyGrupaCPV,
               '_calkowita_wart_zam_od': calkowita_wart_zam_od, '_calkowita_wart_zam_do': calkowita_wart_zam_do, '_cpv_glowny_przedmiot':cpv_glowny_przedmiot, '_numer_ogloszenia':'',
               '_data_publikacjiOd':'', '_data_publikacjiDo':'', '_nazwa_nadana_zamowieniu':'', '_zamawiajacy_nazwa':'', '_zamawiajacy_miejscowosc':'','_zamawiajacy_wojewodztwo':''}
    r = requests.get(url, headers=headers, params=payload)
    text = r.text
    root = ET.fromstring(text)
    root_text = root.text
    output_list = json.loads(root_text)
    return output_list['Table']

def zp400_pobieranie_kryteriow_do_ogloszen(zp400_Guid):
    url = ' http://websrv.bzp.uzp.gov.pl/BZP_PublicWebService.asmx/KryteriaDoZP400_JSON'
    headers = {'content-type': 'text/xml'}
    payload = {'_ZP400Guid': zp400_Guid}
    r = requests.get(url, headers=headers, params=payload)
    text = r.text
    root = ET.fromstring(text)
    root_text = root.text
    output_list = json.loads(root_text)
    return output_list['ZP_400_Kryteria']

def zp400_pobieranie_zalacznikow_do_ogloszen(zp400_Guid):
    url = ' http://websrv.bzp.uzp.gov.pl/BZP_PublicWebService.asmx/ZalacznikiDoZP400_JSON'
    headers = {'content-type': 'text/xml'}
    payload = {'_ZP400Guid': zp400_Guid}
    r = requests.get(url, headers=headers, params=payload)
    text = r.text
    root = ET.fromstring(text)
    root_text = root.text
    output_list = json.loads(root_text)
    return output_list['ZP_400_Zal']


def zp400_pobieranie_kryteriow_do_zalacznikow(zp400_Guid, numer_zalacznika):
    url = ' http://websrv.bzp.uzp.gov.pl/BZP_PublicWebService.asmx/KryteriaZalacznikDoZP400_JSON'
    headers = {'content-type': 'text/xml'}
    payload = {'_ZP400Guid': zp400_Guid, '_numerZalacznika': numer_zalacznika}
    r = requests.get(url, headers=headers, params=payload)
    text = r.text
    root = ET.fromstring(text)
    root_text = root.text
    output_list = json.loads(root_text)
    return output_list['ZP_400_Kryteria']


def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index = False, sheet_name='Sheet1',float_format="%.2f")
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    val = to_excel(df)
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="Your_File.xlsx">Download Excel file</a>' # decode b'abc' => abc


st.write('Zp400_wg_kryteriów:')
wg_kryteriow = zp400_wg_kryteriow('33100000')
main_df = pd.DataFrame(wg_kryteriow)

st.dataframe(main_df, 1000000, 700)
if st.button('Pokaż link do pobrania w xlsx'):
    st.markdown(get_table_download_link(main_df), unsafe_allow_html=True)

st.write("pobieranie_kryteriow_do_ogloszen:")
index = st.text_input('Podaj numer indexu:')

if st.button('Zatwierdź'):
    result = index.title()
    value = main_df.loc[int(result), 'GuidZP400']
    st.write("Pobrane załączniki do ogłoszeń:")
    zalaczniki_do_ogloszenia = zp400_pobieranie_zalacznikow_do_ogloszen(value)
    zalaczniki_do_ogloszenia_df = pd.DataFrame(zalaczniki_do_ogloszenia)
    st.dataframe(zalaczniki_do_ogloszenia_df)

    st.write("Pobrane kryteria do załączników:")
    kryteria_do_zalacznikow = zp400_pobieranie_kryteriow_do_zalacznikow(value, 1)
    kryteria_do_zalacznikow_df = pd.DataFrame(kryteria_do_zalacznikow)
    st.dataframe(kryteria_do_zalacznikow_df)

    st.write("Pobrane kryteria do ogłoszeń:")
    kryteria_do_ogloszenia = zp400_pobieranie_kryteriow_do_ogloszen(value)
    kryteria_do_ogloszenia_df = pd.DataFrame(kryteria_do_ogloszenia)
    st.dataframe(kryteria_do_ogloszenia_df)

st.write('Wyszukiwarka kluczowych słów:')
slowo_klucz = st.text_input('Podaj słowo klucz')
if st.button('Wyszukaj'):
    res = slowo_klucz.title()
    main_filtered_df = main_df[main_df.apply(lambda row: row.astype(str).str.contains(res).any(), axis=1)]
    st.dataframe(main_filtered_df)









