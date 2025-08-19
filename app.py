import streamlit as st
from openai import OpenAI

# --------------- OpenAI Client -----------------
def create_openai_client() -> OpenAI:
    # Reads OPENAI_API_KEY from environment automatically
    return OpenAI()

# --------------- Message Builders --------------
def build_system_messages(explain: bool, clean: bool, style: str, length: str, emojis: bool):
    sys_messages = []

    # Requirement: include a system message exactly as specified
    sys_messages.append({"role": "system", "content": "You are a helpful assistant."})

    rules = [
        "You are a programming joke bot. Always respond with a programming-related joke.",
        "Keep the joke original, witty, and safe for work." if clean else "Keep the joke fun; mild tech sarcasm is okay but avoid hate or harassment.",
        "Keep responses concise." if length == "Short (1-2 lines)" else "You can tell a slightly longer joke (2-5 lines).",
        f"Humor style preference: {style}.",
        "Include a relevant emoji or two." if emojis else "Do not include emojis.",
        "If the user asks for explanation, provide a brief, friendly explanation after the joke."
    ]
    if explain:
        rules.append("Append a short explanation line starting with 'Explanation:'.")

    sys_messages.append({"role": "system", "content": " ".join(rules)})
    return sys_messages

def build_chat_messages(history, user_input, sys_messages):
    messages = []
    messages.extend(sys_messages)
    messages.extend(history)
    if user_input:
        messages.append({"role": "user", "content": user_input})
    return messages

# --------------- OpenAI Call -------------------
def generate_reply(client: OpenAI, model: str, messages, temperature: float, max_tokens: int = 256) -> str:
    response = client.chat.completions.create(
        model=model,  # "gpt-4" or "gpt-3.5-turbo"
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content

# --------------- Session Helpers ---------------
def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []

def reset_conversation():
    st.session_state.messages = []

# --------------- Streamlit UI ------------------
def sidebar_controls():
    st.sidebar.header("JokeBot Settings")
    model = st.sidebar.selectbox(
        "Model",
        options=["gpt-4", "gpt-3.5-turbo"],
        index=0
    )
    temperature = st.sidebar.slider("Creativity (temperature)", 0.0, 1.5, 0.8, 0.05)
    max_tokens = st.sidebar.slider("Max tokens per response", 64, 512, 200, 16)
    style = st.sidebar.selectbox(
        "Humor style",
        ["Witty", "Dry", "Pun-heavy", "Sarcastic (light)", "Wholesome"]
    )
    length = st.sidebar.radio(
        "Preferred length",
        ["Short (1-2 lines)", "Medium (2-5 lines)"],
        index=0
    )
    emojis = st.sidebar.checkbox("Include emojis", value=True)
    explain = st.sidebar.checkbox("Always include a short explanation", value=False)
    clean = st.sidebar.checkbox("Strictly clean jokes (SFW)", value=True)

    if st.sidebar.button("Clear chat", use_container_width=True):
        reset_conversation()

    return {
        "model": model,
        "temperature": float(temperature),
        "max_tokens": int(max_tokens),
        "style": style,
        "length": length,
        "emojis": emojis,
        "explain": explain,
        "clean": clean,
    }

def render_messages():
    if not st.session_state.messages:
        with st.chat_message("assistant"):
            st.write("Hi! I’m your Programming JokeBot. Ask me for a programming joke or give me a topic, language, or framework (e.g., 'Python recursion', 'Git', 'TypeScript generics').")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

def main():
    st.set_page_config(page_title="Programming JokeBot", page_icon="💻")
    st.title("Programming JokeBot 🤖")
    st.caption("A lighthearted chatbot that tells programming jokes.")

    init_session_state()
    settings = sidebar_controls()
    render_messages()

    user_input = st.chat_input("Ask for a programming joke or suggest a topic...")
    if user_input:
        # Append user message
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Build and send
        client = create_openai_client()
        sys_msgs = build_system_messages(
            explain=settings["explain"],
            clean=settings["clean"],
            style=settings["style"],
            length=settings["length"],
            emojis=settings["emojis"],
        )
        messages = build_chat_messages(st.session_state.messages, None, sys_msgs)

        with st.chat_message("assistant"):
            try:
                reply = generate_reply(
                    client=client,
                    model=settings["model"],
                    messages=messages,
                    temperature=settings["temperature"],
                    max_tokens=settings["max_tokens"],
                )
            except Exception as e:
                reply = "Oops! I couldn't fetch a joke right now. Please check your API key and try again."
            st.write(reply)

        # Append assistant reply
        st.session_state.messages.append({"role": "assistant", "content": reply})

if __name__ == "__main__":
    main()