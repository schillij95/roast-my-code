import streamlit as st
from utils.llm import get_model_names, generate_code_roast
from config import ROAST_STYLES, EXAMPLE_SNIPPETS

def init():
    """
    Initialize session state variables for available models and selected model.
    """
    if 'available_models' not in st.session_state:
        st.session_state['available_models'] = get_model_names()
    if 'model' not in st.session_state:
        # Default to the first available model
        st.session_state['model'] = st.session_state['available_models'][0]

@st.dialog("🔥 Roast", width="large")
def response_dialog(generator):
    """
    Display the streaming response from the code roast generator in a dialog.
    """
    response = ""
    with st.empty():
        for chunk in generator:
            response += chunk['response']
            st.write(response)

def on_click_roast_snippet(code_snippet, roast_style, detailed=False):
    """
    Callback for roast buttons. Generates and displays a code roast.
    """
    generator = generate_code_roast(
        code_snippet, 
        detailed=detailed, 
        roast_style=roast_style
    )
    response_dialog(generator)

def model_selection(container):
    """
    Render a model selection dropdown in the given container.
    """
    models = st.session_state['available_models']
    current_model = st.session_state['model']
    model_index = models.index(current_model) if current_model in models else 0
    st.session_state['model'] = container.selectbox(
        "Select LLM Model",
        options=models,
        index=model_index
    )

def roast_style_selection(container):
    """
    Render a roast style selection dropdown in the given container.
    """
    return container.selectbox(
        "Select Roast Style", 
        options=ROAST_STYLES, 
        index=0, 
        accept_new_options=True
    )

def draw_sidebar():
    """
    Draw the sidebar with model and roast style selection.
    """
    model_selection(container=st.sidebar)
    st.session_state['roast_style'] = roast_style_selection(container=st.sidebar)

def draw_example_snippets():
    """
    Render example snippet pills and return the selected snippet's code.
    """
    example_names = [snippet['title'] for snippet in EXAMPLE_SNIPPETS]
    selected_snippet_name = st.pills(
        label='Examples', 
        options=example_names, 
        default=None
    )
    selected_snippet_code = next(
        (snippet['code'] for snippet in EXAMPLE_SNIPPETS if snippet['title'] == selected_snippet_name), 
        ""
    )
    return selected_snippet_code

def draw_page():
    """
    Draw the main page layout with code input and roast buttons.
    """
    st.title("Roast my Code")
    tabs = st.tabs(["Code Snippet", "Github URL"])

    with tabs[0]:
        selected_snippet_code = draw_example_snippets()
        code_snippet = st.text_area(
            "Enter your Code", 
            value=selected_snippet_code, 
            height=300, 
            placeholder="Paste your code snippet here..."
        )
        cols = st.columns(2)
        # Quick Roast button
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
        # Detailed Roast button
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
        st.text_input("Enter the github repository URL")

def main():
    """
    Main entry point for the Streamlit app.
    """
    init()
    draw_sidebar()
    draw_page()

if __name__ == "__main__":
    main()