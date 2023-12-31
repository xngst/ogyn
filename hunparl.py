import re
import pandas as pd

"""
oszággyűlési napló tisztazó modul
"""

def ogy_n_tisztazo(text: str)->str:
    r"""
    eltavolitja:
        - a sorvegi szoelvalasztashoz hasznalt "-" kotojeleket
            peldaul:
                Ország-\n
                gyűlés
                ->
                Országgyűlés!
        - ido jeloleseket,
            peldaul: (9.10)
        - oldalszamokat
            peldaul: 8712
        - oldal fejleceket peldaul:
            "Az Országgyűlés tavaszi ülésszakának 13. ülésnapja,
            2019. április 2-án, kedden"
    """
    dash_pat = re.compile(r'-\n')
    time_stamp_pat = re.compile(r" \n\n \(\d{2}.\d{2}\) \n\n \n")
    page_number_pat = re.compile(r'\n\n\x0c\d{4,5}|\n\n\d{5}')
    header_pat = re.compile(r'\n\nAz Országgyűlés(.*)ülés(.*)\n')

    cleaned_text = re.sub(dash_pat, '', text)
    cleaned_text = re.sub(time_stamp_pat, '', cleaned_text)
    cleaned_text = re.sub(page_number_pat, '', cleaned_text)
    cleaned_text = re.sub(header_pat, '', cleaned_text)

    cleaned_text = cleaned_text.replace("  ", " ").replace("  ", " ")
    cleaned_text = cleaned_text.replace("\n", " ")

    return cleaned_text

def szam(text: str)->str:
    try:
        szam_pat = re.compile(r"\d{2,3}\. szám")
        szam = re.findall(szam_pat, text)
        szam = szam[0].replace(". szám","").strip()
    except IndexError as IE:
        szam_pat = re.compile(r"\d{1,3}/\d{1,2}\. szám")
        szam = re.findall(szam_pat, text)
        szam = szam[0].replace(". szám","").strip()
        pass
    return szam

def ciklus(text: str)->str:
    ciklus_pat = re.compile(r"[\d+]{4,4}-[\d+]{4,4}. országgyűlési ciklus")
    ciklus_result = re.findall(ciklus_pat, text)
    ciklus_clean = ciklus_result[0].replace(". országgyűlési ciklus", "")
    return ciklus_clean

def ules_datum(text: str)->str:
    date_pattern = re.compile(r"([\d+]{4,}\.\s[\w+]{5,10}\s[\d+]{1,2}\.)")
    date_list = re.findall(date_pattern, text)[0]
    return date_list

def elnok_lista(text: str)->list:
    chairman_pattern = re.compile("Napló([\s\S]*?)elnöklete alatt")
    chairman_list = re.findall(chairman_pattern, text)
    try:
       chairman_list = chairman_list[0].split("és")
    except IndexError:
        pass
    chairman_list = [i.strip().replace("\n","") for i in chairman_list]
    return chairman_list

def jegyzo_lista(text: str)->list:
    notary_pattern = re.compile("Jegyzők:([\s\S]*?)Hasáb")
    notary_list = re.findall(notary_pattern, text)
    notary_list = notary_list[0].replace("  ", "")\
    .replace(" \x0c", "").split(",")
    notary_list = [i.strip().replace("\n","") for i in notary_list]
    return notary_list

def torzs_szoveg(text: str)->str:
    first_page = re.compile(r"ELNÖK:")
    ogy_start = re.search(first_page, text).start()
    ogy_end = text.find("ülésnapot bezárom.")
    main_text = text[ogy_start:ogy_end-4]
    return main_text
    
def bevezeto_resz(text: str)->str:
	first_page = re.compile(r"ELNÖK:")
	ogy_start = re.search(first_page, text).start()
	head_text = text[:ogy_start]
	page_number_pat = re.compile(r'\d{5}')
	head_text = head_text.replace("Hasáb","").replace("Viszonválasz:","")
	head_text = re.sub(page_number_pat, '', head_text)
	return head_text

def torveny_javaslat_lista(text: str)->list:
    motion_pattern = re.compile(r"T/\d+")
    motion_list = sorted(list(set(re.findall(motion_pattern, text))))
    return motion_list

def hatarozati_javaslat_lista(text: str)->list:
    proposal_pattern = re.compile(r"H/\d+")
    proposal_list = sorted(re.findall(proposal_pattern, text))
    return proposal_list
    
def search_full_db(text, search_string):
    ""

    search_string = search_string.lower()
    collector_df = pd.DataFrame()

    for i in text:
        result = i[3].lower().count(search_string)
        row_df = pd.DataFrame([i[0],i[1], result]).T
        collector_df = pd.concat([collector_df, row_df])

    collector_df.columns = ["szám", "ülésnap", f"találat"]
    collector_df.reset_index(drop=True, inplace=True)
    
    return collector_df    
    
def vita_lista(text):
    vita_pat = re.compile("[^.]* soron következik [^.]*\.", re.IGNORECASE)
    text = re.sub(r"(\d{4})\.", "", text)
    text = re.sub(r"([IVXLCDM]+)\.", "", text)
    matches = re.findall(vita_pat, text)
    cleaned_list = []
    for m in matches:
        m = m.replace("Tisztelt Országgyűlés!","")
        m = m.replace("Tisztelt Ház!","")
        m = m.replace("Soron következik ","")
        m = m.replace("Most soron következik ","")
        m = m.replace("ma kezdődő ülésünk napirendjének megállapítása.","")
        m = m.replace("Elnök:","")
        m = m.replace(" a lezárásig.","")
        m = m.replace("a  lezárásig.","")
        m = m.replace("„","")
        m = m.replace(".","")
        m = m.strip()
        m = m.capitalize()
        m = m+"."
        cleaned_list.append(m)
        
    return cleaned_list 
    
def vita_szoveg(text):
    vita_pat = re.compile("[^.]* soron következik [^.]*\.", re.IGNORECASE)
    matches = re.findall(vita_pat, text)
    vita_blokk = []
    for i in range(len(matches)):
        try:
            vita_blokk.append(text[text.index(matches[i]):text.index(matches[i+1])])
        except IndexError as ie:
            vita_blokk.append(text[text.index(matches[i]):])
    return vita_blokk  
    
def napirendi_szotar(napirend,vita_szovegek):
    return dict(zip(napirend,vita_szovegek))         

def kepviselo_lista(text: str)->list:
    mp_name_pattern = re.compile(r"(\b[A-Z.ÁÍÉÓÖŐÚÜŰ-]+)"\
                                 r"(\s[A-Z.ÁÍÉÓÖŐÚÜŰ-]+)"\
                                 r"(\s[A-Z.ÁÍÉÓÖŐÚÜŰ-]+)?"\
                                 r"(\s[A-Z.ÁÍÉÓÖŐÚÜŰ-]+)*")
    mp_matches = re.findall(mp_name_pattern, text)
    mp_list = []
    for name in mp_matches:
        joined_name = "".join(name)
        if len(joined_name) > 8:
            mp_list.append(joined_name)
    mp_list = list(sorted(set(mp_list)))
    return mp_list

def kepviseloi_felszolalas_szotar(text: str, mp_list: list)->dict:
    name_dict = {}
    for name in mp_list:
        name_dict[name] = [name.start() for name in re.finditer(name, text)]
    mp_speech_dict = {}
    for name, start_char in name_dict.items():
        if start_char:
            if len(start_char) > 1:
                speech_list = []
                for value in start_char:
                    end_char = text[value:].find("ELNÖK:")
                    speech = text[value:value + end_char]
                    speech_list.append(speech)
                    mp_speech_dict[name] = speech_list
            else:
                end_char = text[start_char[0]:].find("ELNÖK:")
                speech = text[start_char[0]:start_char[0] + end_char]
                mp_speech_dict[name] = speech
    return mp_speech_dict

def reakcio_lista(text: str)->list:
    emot_pat = re.compile(r"\([A-ZÁÍÉÓÖŐÚÜŰ a-z áíéóöőúüű.…,:!?-]+\)")
    emot_list = re.findall(emot_pat, text)
    emot_list = [i for i in emot_list if len(i) > 8]
    return emot_list

def reakcio_szotar(kepviseloi_felszolalas_szotar):
    reakcio_szotar = {}
    for key, value in kepviseloi_felszolalas_szotar.items():
        reakcio_szotar[key] = [reakcio_lista(i) for i in value if reakcio_lista(i)]
    return reakcio_szotar


