import streamlit as st
import streamlit.components.v1 as components
import sqlite3
from pathlib import Path
import hunparl as hp
import sqlite3
import pandas as pd

#db_dir = Path("/home/xn/Script/Streamlit/git/ogyn dev/text")
#root_dir = Path("/home/xn/Script/Streamlit/git/ogyn dev")

root_dir = Path("/app")
db_dir = Path(root_dir/"db")

con = sqlite3.connect(db_dir/"ogyn.db")
cur = con.cursor()

st.header("Országgyűlési napló elemző")
tab1, tab2, tab3 = st.tabs(["Elemző","Kereső","Ismertető"])

with tab1:

	issues_q = cur.execute("select date from ogyn")
	issues = [str(i[0]) for i in issues_q.fetchall()]

	option = st.selectbox('-',issues, index=None, placeholder="Ülésnap")

	if option:
		issue_q = cur.execute(f"select * from ogyn where date = '{option}'")
		issue = issue_q.fetchall()
		full_text = issue[0][3]
		
		ciklus = hp.ciklus(full_text)
		st.write(f"  Ciklus: {ciklus} | Szám: {issue[0][0]}")
		
		elnok_lista = hp.elnok_lista(full_text)
		
		jegyzo_lista = hp.jegyzo_lista(full_text)
		
		hatarozati_javaslat_lista = hp.hatarozati_javaslat_lista(full_text)
		
		bevezeto = hp.bevezeto_resz(full_text)
		
		cleaned = hp.ogy_n_tisztazo(full_text)
		torzs_szoveg = hp.torzs_szoveg(cleaned)
		torveny_javaslat_lista = hp.torveny_javaslat_lista(cleaned)
		
		napirend_lista = hp.vita_lista(cleaned)
		vita_szoveg = hp.vita_szoveg(cleaned)
		napirendi_szotar = hp.napirendi_szotar(napirend_lista,vita_szoveg)
		
		kepviselo_lista = hp.kepviselo_lista(cleaned)
		kepviseloi_felszolalas_szotar = hp.kepviseloi_felszolalas_szotar(cleaned,kepviselo_lista)
		
		reakcio_lista = hp.reakcio_lista(cleaned)	
		reakcio_szotar = hp.reakcio_szotar(kepviseloi_felszolalas_szotar)
		reakcio_szotar_ertekek = {k: v for k, v in reakcio_szotar.items() if len(v) != 0}
		
		with st.expander("Elnök lista"):
			for elnok in elnok_lista:
				st.write(elnok)
				
		with st.expander("Jegyző lista"):
			for jegyzo in jegyzo_lista:
				st.write(jegyzo)
		
		if torveny_javaslat_lista:
			with st.expander("Törvényjavaslatok"):
				for tj in torveny_javaslat_lista:
					st.write(tj)
				
		if hatarozati_javaslat_lista:
			with st.expander("Határozati javaslatok"):
				for hatarozat in hatarozati_javaslat_lista:
					st.write(hatarozat)	
		
		st.divider()	
		st.write("Napirendi pontok:")
			
		for i, napirend in enumerate(napirend_lista):
			with st.expander(f"{napirend}"):
				st.write(napirendi_szotar[napirend])
					
		with st.expander("Bevezető szöveg"):
			st.write(bevezeto.replace(".",""))
		
		with st.expander("Törzsszöveg"):
			components.html(
				f"""
				<div style="color:#ffffff">{torzs_szoveg}</div>""",
				height=600,
				scrolling=True,
			)
			
		kepviselo = st.selectbox('-',
			kepviselo_lista, 
			index=None,
			placeholder="Kéviselők felszólalásai")
		
		if kepviselo:
			hozzaszolasok = kepviseloi_felszolalas_szotar[kepviselo]
			hozzaszolasok_szama = len(hozzaszolasok)
			
			if type(hozzaszolasok) == list:
				st.subheader(f"{kepviselo} {hozzaszolasok_szama} hozzászólással élt:")
				for index, felsz in enumerate(hozzaszolasok):
					st.subheader(f"{index+1}.")
					st.write(felsz)
			else:
				st.subheader(f"{kepviselo} 1 hozzászólással élt:")
				st.write(hozzaszolasok)
				
		kepviselo = st.selectbox('-',
			reakcio_szotar_ertekek.keys(), 
			index=None,
			placeholder="Felszólalások reakciói")
			
		if kepviselo:
			reakcio_szotar = hp.reakcio_szotar(kepviseloi_felszolalas_szotar)
			reakciok = reakcio_szotar[kepviselo]
			for index, reakcio in enumerate(reakciok):
				st.write(f"{index+1}.:")
				for elem in reakcio:
					st.write(elem)

with tab2:
	con = sqlite3.connect(db_dir/"ogyn.db")
	cur = con.cursor()
	
	min_date_q = cur.execute("SELECT date FROM ogyn WHERE id = (SELECT MIN(id) FROM ogyn)")
	min_date = min_date_q.fetchall()
	st.write(f"Legelső elérhető ülésnap az adatbázisban: {min_date[0][0]}")
	
	max_date_q = cur.execute("SELECT date FROM ogyn WHERE id = (SELECT MAX(id) FROM ogyn)")
	max_date = max_date_q.fetchall()
	st.write(f"Legutolsó elérhető ülésnap az adatbázisban: {max_date[0][0]}")	
	
	full_res = cur.execute("SELECT * FROM ogyn")
	text = full_res.fetchall()
	
	text_input = None
	
	substring = st.toggle('Keresés részszavakban')

	text_input = st.text_input("Keresés az egész adatbázisban")
    
	if text_input:
		if not substring:
			text_input = " " + text_input + " "
		df = hp.search_full_db(text,text_input)
		st.markdown(f"{df['találat'].sum()} találat a **'{text_input}'** szóra")
		df.set_index("ülésnap",drop=True,inplace=True)
		st.bar_chart(df[["találat"]])
		st.dataframe(df)

				
with tab3:	
	with open(root_dir/'ismerteto.txt','r') as f:
		ismerteto = f.read()
		st.write(ismerteto)

	
