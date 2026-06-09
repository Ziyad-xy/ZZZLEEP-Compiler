import streamlit as st
import subprocess
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_FILE = os.path.join(BASE_DIR, "examplescanner2.txt")
MAIN_FILE = os.path.join(BASE_DIR, "main.py")

st.set_page_config(page_title="Sleep Language Compiler", layout="wide")

st.title("😴 Sleep Language Compiler")

code = st.text_area("Enter Sleep Language Code", height=350)

if st.button("Run Compiler"):
    if not code.strip():
        st.warning("Please enter some code first.")
    else:
        with open(SOURCE_FILE, "w", encoding="utf-8") as f:
            f.write(code)

        result = subprocess.run(
            [sys.executable, MAIN_FILE],
            capture_output=True,
            text=True,
            cwd=BASE_DIR
        )

        output = (result.stdout + "\n" + result.stderr).strip()

        st.subheader("Compiler Result")

        if "Semantic Errors" in output and "No errors" not in output:
            st.error("❌ Semantic Errors Found")
            errors = []
            for line in output.splitlines():
                if line.strip().startswith("•"):
                    errors.append(line.strip())

            if errors:
                for e in errors:
                    st.write(e)
            else:
                st.text(output)

        elif "No errors" in output:
            st.success("✅ Compilation Successful — No Semantic Errors")
            with st.expander("View Compiler Output"):
                st.text(output)

        else:
            st.warning("⚠️ Compiler produced unexpected output")
            st.text(output)
