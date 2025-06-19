import streamlit as st
from utils.llm import get_model_names, generate_code_roast
from utils.parser import parse_full_github_user, parse_repo
from utils.summarize_git import critique_code_dict
from config import ROAST_STYLES, EXAMPLE_SNIPPETS, VOICES, DEFAULT_VOICE
import torch

torch.classes.__path__ = [] # hack to satisfy torch within docker madness


def init():
    """
    Initialize session state variables for available models and selected model.
    """
    if 'available_models' not in st.session_state:
        st.session_state['available_models'] = get_model_names()
    if 'model' not in st.session_state:
        # Default to the first available model
        st.session_state['model'] = st.session_state['available_models'][0]
    if 'voice_output' not in st.session_state:
        st.session_state['voice_output'] = False
    if 'voice' not in st.session_state:
        st.session_state['voice'] = DEFAULT_VOICE

@st.dialog("🔥 Roast", width="large")
def response_dialog(generator):
    """
    Display the streaming response from the code roast generator in a dialog.
    """
    if st.session_state['voice_output']:
        from utils.speech import stream_text_and_speech_generator
        stream_text_and_speech_generator(generator)
    else:
        response = ""
        with st.empty():
            for chunk in generator:
                response += chunk['response']
                st.write(response)

def on_click_roast_snippet(code_snippet_fn, roast_style, detailed=False, type="code snippet"):
    """
    Callback for roast buttons. Generates and displays a code roast.
    """
    code_snippet = code_snippet_fn(detailed)
    generator = generate_code_roast(
        code_snippet, 
        detailed=detailed, 
        roast_style=roast_style,
        type=type
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
    # Show only style names in the dropdown, but return name plus description for the LLM
    names = [r['name'] for r in ROAST_STYLES]
    selected = container.selectbox(
        "Select Roast Style",
        options=names,
        index=0,
        accept_new_options=True
    )
    style = next((r for r in ROAST_STYLES if r['name'] == selected), None)
    if style:
        return f"{style['name']} ({style['description']})"
    return selected

def draw_sidebar():
    """
    Draw the sidebar with model and roast style selection.
    """
    model_selection(container=st.sidebar)
    st.session_state['roast_style'] = roast_style_selection(container=st.sidebar)
    st.session_state['voice_output'] = st.sidebar.toggle(
        "Enable Voice Output",
        value=st.session_state['voice_output'],
        help="Enable this to hear the roast read aloud."
    )
    if st.session_state['voice_output']:
        st.session_state['voice'] = st.sidebar.selectbox(
            "Select Voice",
            options=VOICES,
            index=VOICES.index(DEFAULT_VOICE) if DEFAULT_VOICE in VOICES else 0
        )

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

def draw_roast_buttons(code_snippet_fn, key):
    cols = st.columns(2)
    # Quick Roast button
    cols[0].button(
        "Quick Roast", 
        use_container_width=True, 
        on_click=on_click_roast_snippet, 
        kwargs={
            'code_snippet_fn': code_snippet_fn,
            'roast_style': st.session_state['roast_style'],
            'detailed': False,
            'type': key
        },
        key=f"quick_roast_{key}"
    )
    # Detailed Roast button
    cols[1].button(
        "Detailed Roast", 
        use_container_width=True, 
        on_click=on_click_roast_snippet, 
        kwargs={
            'code_snippet_fn': code_snippet_fn,
            'roast_style': st.session_state['roast_style'],
            'detailed': True,
            'type': key
        },
        key=f"detailed_roast_{key}"
    )

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
        draw_roast_buttons(code_snippet_fn=lambda _: code_snippet, key="code snippet")     
    with tabs[1]:
        st.write("Enter the URL of your GitHub repository containing the code you want to roast.")
        profile = st.text_input("Enter the github profile name", placeholder="schillij95")
        repository = st.text_input("Enter the github repository name (optional)", placeholder="roast-my-code")
        if profile:
            st.write(f"Fetching code from GitHub profile: {profile}")
            def code_snippet_fn(detailed=False):
                def helper():
                    if not repository:
                        code_dict = parse_full_github_user(profile, depth=0 if not detailed else 1)
                    else:
                        code_dict = parse_repo(profile, repository, depth=1 if not detailed else 2)
                    summary = critique_code_dict(code_dict)
                    st.session_state['github_profile'] = profile
                    st.session_state['github_profile_summary'] = summary
                    st.session_state['detailed'] = detailed
                    st.session_state['repository'] = repository
                    return summary
                if ('github_profile' not in st.session_state or st.session_state['github_profile'] != profile) \
                        or ('github_profile_summary' not in st.session_state or not st.session_state['github_profile_summary']) \
                        or (detailed and ('detailed' not in st.session_state or not st.session_state['detailed'])) \
                        or ('repository' not in st.session_state or st.session_state['repository'] != repository):
                    summary = helper()
                else:
                    summary = st.session_state['github_profile_summary']
                # dict to string conversion for display
                code_snippet = "\n".join(f"{k}: {v}" for k, v in summary.items()) + "\nSummary for the user {profile}:".format(profile=profile)
                return code_snippet
            draw_roast_buttons(code_snippet_fn=code_snippet_fn, key="github profile")
        


def main():
    """
    Main entry point for the Streamlit app.
    """
    init()
    draw_sidebar()
    draw_page()

if __name__ == "__main__":
    main()