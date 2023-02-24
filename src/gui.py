__version__ = "Beta"

import base64

app_name = "Ask FAR"


# BOILERPLATE
import csv
import streamlit as st
import pandas as pd
import time
api_key = st.secrets["API_KEY"] 

st.set_page_config(layout='centered', page_title=f'{app_name} {__version__}',initial_sidebar_state="collapsed")
ss = st.session_state
if 'debug' not in ss: ss['debug'] = {}
import css
st.write(f'<style>{css.v1}</style>', unsafe_allow_html=True)
header1 = st.empty() # for errors / messages
header2 = st.empty() # for errors / messages
header3 = st.empty() # for errors / messages

# IMPORTS

import prompts
import model

# COMPONENTS

def ui_spacer(n=2, line=False, next_n=0):
	for _ in range(n):
		st.write('')
	if line:
		st.tabs([' '])
	for _ in range(next_n):
		st.write('')



def index_pdf_file2():
	import pickle
	with open("src/index.pkl", "rb") as f:
		out = pickle.load(f)
	index = out

	ss['index'] = index
	ss['debug']['n_pages'] = len(index['pages'])
	ss['debug']['n_texts'] = len(index['texts'])
	ss['debug']['pages'] = index['pages']
	ss['debug']['texts'] = index['texts']
	ss['debug']['summary'] = index['summary']



def ui_question():
	st.title('First Came the FAR, Then Came FARGPT')
	st.header('Why FARGPT and why not ChatGPT?')
	st.subheader('FARGPT is built to semantically search the FAR and provide answers and references whereas ChatGPT searches its entire collection of text to find answers which may not be related to the FAR at all.')
	st.write('## Ask the FAR a Question!')
	st.text_area('question', key='question', height=100, placeholder='Enter question here', help='', label_visibility="collapsed", disabled=False)

# REF: Hypotetical Document Embeddings

def ui_output():
	output = ss.get('output','')
	st.markdown(output)

def ui_debug():
	if ss.get('show_debug'):
		st.write('### debug')
		st.write(ss.get('debug',{}))


def b_ask():
	disabled = False
	if st.button('Submit', disabled=disabled, type='primary'):
		text = ss.get('question','')
		temperature = ss.get('temperature', 0.0)
		hyde = ss.get('use_hyde')
		hyde_prompt = ss.get('hyde_prompt')
		if ss.get('use_hyde_summary'):
			summary = ss['index']['summary']
			hyde_prompt += f" Context: {summary}\n\n"
		task = ss.get('task')
		max_frags = ss.get('max_frags',1)
		index = ss.get('index',{})
		with st.spinner('preparing answer'):

			resp = model.query(text, index, task=Task, temperature=temperature, hyde=hyde, hyde_prompt=hyde_prompt, max_frags=max_frags, limit=max_frags+2)
		ss['debug']['model.query.resp'] = resp
		
		q = text.strip()
		a = resp['text'].strip()
		output_add(q,a)

def b_clear():
	if st.button('clear output'):
		ss['output'] = ''

def b_reindex():
	if st.button('reindex'):
		index_pdf_file()

def b_reload():
	if st.button('reload prompts'):
		import importlib
		importlib.reload(prompts)

def write_in_csv(q,a):
	file_path = "src/QAcsv.csv"
	with open(file_path, 'a', newline='\n') as file:
		writer = csv.writer(file)

		writer.writerow([str(q), str(a)])
		print("writing in csv")
	file.close()
		
def output_add(q, a):
	print(a)
	write_in_csv(q, a)
	t = st.empty()
	if 'output' not in ss:
		ss['output'] = ""
	new = f'#### {q}\n\n'
	ss['output']=ss['output']+new
	for i in a:
		
		ss['output'] = ss['output'] + i
		t.write(ss['output'])
		time.sleep(0.01)

	#print('\n', flush=True)




# LAYOUT



Task = "Answer the question truthfully based on the text below. Include verbatim quote and a comment where to find it in the text (page number). After the quote write a step by step explanation. Use bullet points. "
api_key = st.secrets["API_KEY"]
model.use_key(api_key)
secret_key = st.secrets["password"]



index_pdf_file2()
#ui_pdf_file()


def page2():

	# Load CSV file into a pandas DataFrame
	df = pd.read_csv('src/QAcsv.csv')

	# Display the DataFrame in Streamlit
	st.write(df)
	csv = df.to_csv(index=False)
	b64 = base64.b64encode(csv.encode()).decode()

	href = f'<a href="data:file/csv;base64,{b64}" download="QAcsv.csv">Download CSV file</a>'
	st.markdown(href, unsafe_allow_html=True)

timer = 1
def app():
	global timer
	st.sidebar.beta_expander("Navigation", expanded=False)
	selection = st.sidebar.radio("Go to", ["Public", "Admin"], index=0)
	if selection == "Admin":
		provided_key = st.text_input("Enter the secret key to access this page:",type="password")
		if provided_key != secret_key:
			timer += 1
			time.sleep(timer)
			st.write("Incorrect key. You do not have access to this page.")
			return
	timer = 1
	# Run the selected page
	if selection == "Public":
		ui_question()

		b_ask()
		#b_clear()
		#ui_output()
	elif selection == "Admin":
		page2()
app()

