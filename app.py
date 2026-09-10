import os
import re
import streamlit as st
from query import query

st.set_page_config(page_title="Datasheet Assistant", page_icon="🔀")

st.title("Datasheet Assistant")
st.caption("Grounded answers to switch specification questions, cited to source.")


def pretty_source(path):
    """Pull the model out of whatever the vendor named the PDF.

    'qfx5130-line-of-switches-datasheet.pdf'          -> QFX5130 (QFX Series)
    'Juniper Networks EX2300 Switch-a00151236enw.pdf' -> EX2300 (EX Series)

    Filename rather than folder, because downloaded datasheets rarely land
    in a tidy directory structure.
    """
    name  = os.path.splitext(os.path.basename(path))[0]
    match = re.search(r"\b(qfx|ex)[\s_-]*(\d{4}[a-z0-9-]{0,4})", name, re.I)
    if not match:
        return name
    family = match.group(1).upper()
    model  = match.group(2).upper().rstrip("-")
    return f"{family}{model} ({family} Series)"


if "messages" not in st.session_state:
    st.session_state.messages = []

# Empty state — the app is otherwise a blank void before the first question.
if not st.session_state.messages:
    st.markdown(
        """
        <div style="margin-top:2.5rem;padding:1.5rem 0;border-top:1px solid #2a2f3a">
          <div style="font-size:.75rem;letter-spacing:.12em;text-transform:uppercase;
                      color:#6b7280;margin-bottom:1rem">Try asking</div>
          <div style="color:#9ca3af;line-height:2;font-size:.95rem">
            How many 10GbE ports does the QFX5100 have?<br>
            Compare uplink options on the QFX5100 and the QFX5130.<br>
            Does the EX2300 support PoE+, and on how many ports?<br>
            What is the switching capacity of the QFX5130?
          </div>
          <div style="margin-top:1.75rem;font-size:.8rem;color:#4b5563">
            Answers come only from the ingested EX and QFX datasheets.
            If a spec isn't in them, the assistant says so rather than guessing.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about a switch specification..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching datasheets..."):
            answer, sources = query(prompt)
        st.markdown(answer)
        if sources:
            with st.expander(f"Sources ({len(set(sources))})"):
                for s in dict.fromkeys(sources):
                    st.write(f"- {pretty_source(s)}")

    st.session_state.messages.append({"role": "assistant", "content": answer})
