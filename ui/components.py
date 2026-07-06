import streamlit as st


def render_result_download(label: str, data: bytes, file_name: str, mime: str) -> None:
    st.success("Process completed successfully.")
    st.download_button(
        label=label,
        data=data,
        file_name=file_name,
        mime=mime,
        use_container_width=True,
    )


def render_error_report(errors: list[dict]) -> None:
    if not errors:
        return
    st.subheader("Error Report")
    st.dataframe(errors, use_container_width=True, hide_index=True)
