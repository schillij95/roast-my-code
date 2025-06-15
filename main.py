import streamlit as st
from llm import get_installed_models, generate_code_roast
from config import ROAST_STYLES, EXAMPLE_SNIPPETS

def init():
    if 'available_models' not in st.session_state:
        st.session_state['available_models'] = get_installed_models()
    if 'model' not in st.session_state:
        st.session_state['model'] = st.session_state['available_models']

@st.dialog("🔥 Roast", width="large")
def response_dialog(generator):
    response = ""
    with st.empty():
        for chunk in generator:
            response += chunk['response']
            st.write(response)

def on_click_roast_snippet(code_snippet, roast_style, detailed=False):
    generator = generate_code_roast(code_snippet, detailed=detailed, roast_style=roast_style)
    response_dialog(generator)
    

def model_selection(container):
    models = st.session_state['available_models']
    model_index = models.index(st.session_state['model']) if st.session_state['model'] in models else 0
    st.session_state['model'] = container.selectbox(
        "Select LLM Model",
        options=models,
        index=model_index
    )

def roast_style_selection(container):
    return container.selectbox("Select Roast Style", options=ROAST_STYLES, index=0, accept_new_options=True)

def draw_sidebar():
    model_selection(container=st.sidebar)
    st.session_state['roast_style'] = roast_style_selection(container=st.sidebar)

def draw_example_snippets():
    example_names = [snippet['title'] for snippet in EXAMPLE_SNIPPETS]
    selected_snippet_name = st.pills(label='Examples', options=example_names, default=None)
    selected_snippet_code = next((snippet['code'] for snippet in EXAMPLE_SNIPPETS if snippet['title'] == selected_snippet_name), "")
    return selected_snippet_code

def draw_page():
    st.title("Roast my Code")
    
    tabs = st.tabs(["Code Snippet", "Github URL"])
    
    with tabs[0]:
        selected_snippet_code = draw_example_snippets()
        code_snippet = st.text_area("Enter your Code", value=selected_snippet_code, height=300, placeholder="Paste your code snippet here...")
        cols = st.columns(2)
        cols[0].button(
            "Quick Roast", 
            use_container_width=True, 
            on_click=on_click_roast_snippet, 
            kwargs={
                'code_snippet': code_snippet,
                'roast_style': st.session_state['roast_style'],
                'detailed': False
            },
            disabled=not code_snippet.strip()
        )
        cols[1].button(
            "Detailed Roast", 
            use_container_width=True, 
            on_click=on_click_roast_snippet, 
            kwargs={
                'code_snippet': code_snippet,
                'roast_style': st.session_state['roast_style'],
                'detailed': True
            },
            disabled=not code_snippet.strip()
        )
    with tabs[1]:
        st.write("Enter the URL of your GitHub repository containing the code you want to roast.")
        github_repo = st.text_input("Enter the github repository URL")

def main():
    init()
    draw_sidebar()
    draw_page()

if __name__ == "__main__":
    main()